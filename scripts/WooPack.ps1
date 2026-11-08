# Transactional installer/uninstaller for the Woo Storm 4 modpack.
# It copies only the game payload, backs up every file it replaces, and records
# SHA-256 hashes in .woopack-manifest.json so Uninstall can restore the originals
# and preserve post-install edits as *.woopack-displaced.
# Default log: %LOCALAPPDATA%\SenjuWoo\WooPack\install.log
[CmdletBinding()]
param(
    [ValidateSet('Install', 'Uninstall')]
    [string]$Action = 'Install',
    [string]$SourcePath,
    [string]$GamePath,
    [string]$LogPath,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$ManifestName = '.woopack-manifest.json'
$BackupName = '_WooPack_Backup'
$PayloadDirs = @('character', 'data', 'data_win32', 'moddingapi')
$PayloadFiles = @('d3dcompiler_47.dll', 'd3dcompiler_47_o.dll')
$TestedExeHash = '147e52a3e0d7382501a6777e158b37908e0b69d4e902079dc6e62dcae69bc257'
$script:LogPath = $null


# Write one timestamped line to the console and, when enabled, the log file.
function Write-Log {
    param([string]$Message)
    $line = '{0} {1}' -f (Get-Date).ToUniversalTime().ToString('o'), $Message
    Write-Host $Message
    if ($script:LogPath) {
        [System.IO.File]::AppendAllText($script:LogPath, $line + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
    }
}


# Turn a normal path into a \\?\ path so nested .xfbin paths survive MAX_PATH.
function Get-LongPath {
    param([string]$Path)
    $Path = $Path -replace '/', '\'
    if ($Path.StartsWith('\\?\')) { return $Path }
    if ($Path.StartsWith('\\')) { return '\\?\UNC\' + $Path.Substring(2) }
    return '\\?\' + $Path
}


# Normalize a user-supplied path once; the rest of the script uses long paths.
function Get-NormalizedPath {
    param([string]$Path)
    return ([System.IO.Path]::GetFullPath($Path)).TrimEnd('\')
}


function Test-FileExists {
    param([string]$Path)
    return [System.IO.File]::Exists((Get-LongPath $Path))
}


function Test-DirExists {
    param([string]$Path)
    return [System.IO.Directory]::Exists((Get-LongPath $Path))
}


# A manifest path must stay a relative path inside the selected game folder.
function Test-SafeRelativePath {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    if ([System.IO.Path]::IsPathRooted($Path)) { return $false }
    $parts = $Path -split '[\\/]'
    if ($parts -contains '..' -or $parts -contains '.') { return $false }
    return $true
}


# Resolve a manifest/payload relative path and reject any escape from Game.
function Get-SafeDestination {
    param([string]$Game, [string]$Relative)
    if (-not (Test-SafeRelativePath $Relative)) { throw "Unsafe relative path in manifest: $Relative" }
    $destination = [System.IO.Path]::GetFullPath((Join-Path $Game $Relative))
    if (-not $destination.StartsWith($Game + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escapes the game folder: $Relative"
    }
    return $destination
}


function Get-FileSize {
    param([string]$Path)
    return [System.IO.FileInfo]::new((Get-LongPath $Path)).Length
}


# Hash a file without loading it into memory. Works with \\?\ paths.
function Get-Sha256 {
    param([string]$Path)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $stream = [System.IO.File]::Open((Get-LongPath $Path), [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
        try { return ([BitConverter]::ToString($sha.ComputeHash($stream)) -replace '-', '').ToLowerInvariant() }
        finally { $stream.Dispose() }
    }
    finally { $sha.Dispose() }
}


# Resolve the Steam library that contains App 349040, or return $null.
function Find-GamePath {
    $candidates = New-Object System.Collections.Generic.List[string]
    $steam = $null
    foreach ($key in @('HKCU:\Software\Valve\Steam', 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam', 'HKLM:\SOFTWARE\Valve\Steam')) {
        if (Test-Path $key) {
            $props = Get-ItemProperty -Path $key -ErrorAction SilentlyContinue
            foreach ($name in @('SteamPath', 'InstallPath')) {
                if ($props -and $props.PSObject.Properties.Name -contains $name -and $props.$name) { $steam = $props.$name; break }
            }
        }
        if ($steam) { break }
    }
    if ($steam) {
        $steam = $steam -replace '/', '\'
        $candidates.Add((Join-Path $steam 'steamapps\common\NARUTO SHIPPUDEN Ultimate Ninja STORM 4'))
        $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf) {
            foreach ($line in Get-Content -LiteralPath $vdf) {
                if ($line -match '"path"\s+"([^"]+)"') {
                    $library = ($Matches[1] -replace '\\\\', '\') -replace '/', '\'
                    $candidates.Add((Join-Path $library 'steamapps\common\NARUTO SHIPPUDEN Ultimate Ninja STORM 4'))
                }
            }
        }
    }
    foreach ($candidate in $candidates) {
        if (Test-FileExists (Join-Path $candidate 'NSUNS4.exe')) { return (Get-NormalizedPath $candidate) }
    }
    return $null
}


# Accept either the extracted "Naruto To Boruto 2.0" folder or its parent.
function Resolve-PackRoot {
    param([string]$Path)
    if (-not $Path) { throw 'SourcePath is required for Install.' }
    $Path = Get-NormalizedPath $Path
    if (-not (Test-DirExists $Path)) { throw "SourcePath not found: $Path" }
    $nested = Join-Path $Path 'Naruto To Boruto 2.0'
    if (Test-DirExists (Join-Path $nested 'moddingapi')) { return $nested }
    if (Test-DirExists (Join-Path $Path 'moddingapi')) { return $Path }
    throw "SourcePath does not look like the pack: missing moddingapi. Point it at the extracted 'Naruto To Boruto 2.0' folder or its parent."
}


# Build the exact payload list: the four game folders plus the two compiler DLLs.
# Save File, Credits.txt and Installation_Instructions.txt stay out of the game root.
function Get-PayloadFiles {
    param([string]$Root)
    $result = New-Object System.Collections.Generic.List[object]
    foreach ($dir in $PayloadDirs) {
        $full = Join-Path $Root $dir
        if (-not (Test-DirExists $full)) { throw "Pack payload folder missing: $dir" }
        $longRoot = (Get-LongPath $full).TrimEnd('\')
        foreach ($file in [System.IO.Directory]::EnumerateFiles($longRoot, '*', [System.IO.SearchOption]::AllDirectories)) {
            $relative = $dir + $file.Substring($longRoot.Length)
            $result.Add([pscustomobject]@{ Relative = $relative; FullName = $file })
        }
    }
    foreach ($name in $PayloadFiles) {
        $full = Join-Path $Root $name
        if (-not (Test-FileExists $full)) { throw "Pack payload file missing: $name" }
        $result.Add([pscustomobject]@{ Relative = $name; FullName = (Get-LongPath $full) })
    }
    return $result
}


# Copy the payload, moving every existing destination into the backup folder first.
function Install-Pack {
    param([string]$Game, [string]$Source)
    $manifestPath = Join-Path $Game $ManifestName
    if (Test-FileExists $manifestPath) { throw "A WooPack manifest already exists. Run Uninstall first: $manifestPath" }
    if (-not (Test-FileExists (Join-Path $Game 'NSUNS4.exe'))) { throw "NSUNS4.exe not found in $Game. Point -GamePath at the Steam game folder." }

    $payload = @(Get-PayloadFiles $Source)
    if ($payload.Count -eq 0) { throw 'Pack payload is empty.' }
    foreach ($item in $payload) { [void](Get-SafeDestination $Game $item.Relative) }

    $sourceBytes = 0
    $backupBytes = 0
    $replaced = 0
    foreach ($item in $payload) {
        $sourceBytes += Get-FileSize $item.FullName
        $destination = Join-Path $Game $item.Relative
        if (Test-FileExists $destination) {
            $backupBytes += Get-FileSize $destination
            $replaced++
        }
    }

    $drive = New-Object System.IO.DriveInfo([System.IO.Path]::GetPathRoot($Game))
    $needed = $sourceBytes + $backupBytes + 256MB

    if ($DryRun) {
        Write-Log ("Dry run: would install {0} files ({1:N0} bytes) from {2} to {3}; {4} existing files would be backed up. Need {5:N0} bytes free, have {6:N0}." -f $payload.Count, $sourceBytes, $Source, $Game, $replaced, $needed, $drive.AvailableFreeSpace)
        return
    }

    if ($drive.AvailableFreeSpace -lt $needed) {
        throw ('Not enough free space on {0}: need {1:N0} bytes, have {2:N0}.' -f $drive.Name, $needed, $drive.AvailableFreeSpace)
    }

    $exeHash = Get-Sha256 (Join-Path $Game 'NSUNS4.exe')
    if ($exeHash -ne $TestedExeHash) {
        Write-Warning "NSUNS4.exe SHA-256 is $exeHash, not the tested $TestedExeHash. The pack was verified on that build; continue only if you accept the mismatch."
    }

    $backupRoot = Join-Path $Game $BackupName
    if (Test-DirExists $backupRoot) {
        throw "A pre-existing $BackupName folder exists in $Game. Move it away; WooPack will not overwrite or delete an unowned backup folder."
    }

    # Record the plan before touching the game: a crash mid-copy still leaves a
    # manifest that Uninstall can use to restore originals and remove partial copies.
    $manifest = [ordered]@{
        schema = 2
        pack = 'Woo Modpack v1.0.0'
        state = 'installing'
        started_at = (Get-Date).ToUniversalTime().ToString('o')
        game_path = $Game
        source_path = $Source
        files = @()
        backups = @()
    }

    foreach ($item in $payload) {
        $destination = Join-Path $Game $item.Relative
        $hadBackup = Test-FileExists $destination
        if ($hadBackup) {
            $manifest.backups += [ordered]@{ path = $item.Relative; sha256 = (Get-Sha256 $destination); size = (Get-FileSize $destination) }
        }
        $manifest.files += [ordered]@{
            path = $item.Relative
            sha256 = (Get-Sha256 $item.FullName)
            size = (Get-FileSize $item.FullName)
            had_backup = $hadBackup
        }
    }

    $json = $manifest | ConvertTo-Json -Depth 6
    [System.IO.File]::WriteAllText((Get-LongPath $manifestPath), $json, (New-Object System.Text.UTF8Encoding($false)))

    for ($index = 0; $index -lt $payload.Count; $index++) {
        $item = $payload[$index]
        $entry = $manifest.files[$index]
        $destination = Join-Path $Game $item.Relative
        $destinationDir = Split-Path -Parent $destination
        if (-not (Test-DirExists $destinationDir)) { [void][System.IO.Directory]::CreateDirectory((Get-LongPath $destinationDir)) }

        if ($entry.had_backup) {
            $backup = Join-Path $backupRoot $item.Relative
            $backupDir = Split-Path -Parent $backup
            if (-not (Test-DirExists $backupDir)) { [void][System.IO.Directory]::CreateDirectory((Get-LongPath $backupDir)) }
            [System.IO.File]::Move((Get-LongPath $destination), (Get-LongPath $backup))
        }

        [System.IO.File]::Copy($item.FullName, (Get-LongPath $destination), $true)
        if ((Get-Sha256 $destination) -ne $entry.sha256) { throw "Installed file hash mismatch: $destination" }
    }

    $manifest.state = 'complete'
    $manifest.completed_at = (Get-Date).ToUniversalTime().ToString('o')
    $json = $manifest | ConvertTo-Json -Depth 6
    [System.IO.File]::WriteAllText((Get-LongPath $manifestPath), $json, (New-Object System.Text.UTF8Encoding($false)))
    Write-Log ("Installed {0} files; backed up {1} replaced file(s) to {2}." -f $payload.Count, $manifest.backups.Count, $backupRoot)
}


# Remove pack-owned files, preserve edits, then restore and verify every backup.
# Missing or corrupt backups block the rollback before any file is changed; the
# manifest and remaining backups are kept for manual recovery.
function Uninstall-Pack {
    param([string]$Game)
    $manifestPath = Join-Path $Game $ManifestName
    if (-not (Test-FileExists $manifestPath)) { throw "No WooPack manifest found in $Game. Nothing to uninstall." }
    $manifest = [System.IO.File]::ReadAllText((Get-LongPath $manifestPath)) | ConvertFrom-Json
    if ($manifest.schema -ne 2) { throw "Unsupported WooPack manifest schema: $($manifest.schema)." }
    if (-not $manifest.game_path) { throw "Manifest has no game_path." }
    if ((Get-NormalizedPath $manifest.game_path) -ne $Game) { throw "Manifest belongs to $($manifest.game_path), not $Game." }
    if (-not $manifest.files -or @($manifest.files).Count -eq 0) { throw "Manifest has no file list." }

    # Validate every path before any destructive operation.
    foreach ($entry in @($manifest.files) + @($manifest.backups)) {
        if ($null -eq $entry) { continue }
        [void](Get-SafeDestination $Game $entry.path)
    }

    $backupRoot = Join-Path $Game $BackupName
    $removed = 0
    $displaced = 0
    $missing = 0
    $restored = 0
    $incomplete = 0
    $backupPaths = @{}
    foreach ($backupEntry in @($manifest.backups)) {
        if ($null -ne $backupEntry) { $backupPaths[$backupEntry.path] = $backupEntry }
    }

    if ($DryRun) {
        Write-Log ("Dry run: would remove {0} pack-owned files and restore {1} backups in {2}." -f @($manifest.files).Count, $backupPaths.Count, $Game)
        return
    }

    # Preflight: never start a rollback that cannot restore an original.
    # A missing backup is acceptable only when the original is still in place
    # (the interrupted-install case), never when it would lose the original.
    $alreadyInPlace = @{}
    foreach ($backupEntry in $backupPaths.Values) {
        $backup = Join-Path $backupRoot $backupEntry.path
        $destination = Get-SafeDestination $Game $backupEntry.path
        $backupOk = (Test-FileExists $backup) -and ((Get-Sha256 $backup) -eq $backupEntry.sha256)
        if (-not $backupOk) {
            if ((Test-FileExists $destination) -and ((Get-Sha256 $destination) -eq $backupEntry.sha256)) {
                $alreadyInPlace[$backupEntry.path] = $true
            } else {
                Write-Warning "Required backup is missing or corrupt: $backup"
                $incomplete++
            }
        }
    }
    if ($incomplete -gt 0) {
        Write-Log ("Rollback blocked: {0} required backup(s) are missing or corrupt; manifest and backups kept." -f $incomplete)
        throw "Rollback incomplete; no game files were changed."
    }

    foreach ($entry in @($manifest.files)) {
        if ($null -eq $entry) { continue }
        $destination = Get-SafeDestination $Game $entry.path
        $backup = Join-Path $backupRoot $entry.path
        $hadBackup = $false
        if ($entry.PSObject.Properties.Name -contains 'had_backup') { $hadBackup = [bool]$entry.had_backup }
        elseif ($backupPaths.ContainsKey($entry.path)) { $hadBackup = $true }

        if ($alreadyInPlace.ContainsKey($entry.path)) { continue }
        if ($hadBackup -and -not (Test-FileExists $backup)) {
            Write-Warning "Backup disappeared during rollback: $backup"
            $incomplete++
            continue
        }

        if (Test-FileExists $destination) {
            if ((Get-Sha256 $destination) -eq $entry.sha256) {
                [System.IO.File]::Delete((Get-LongPath $destination))
                $removed++
            } else {
                $target = $destination + '.woopack-displaced'
                $index = 1
                while (Test-FileExists $target) { $target = $destination + '.woopack-displaced.' + $index; $index++ }
                [System.IO.File]::Move((Get-LongPath $destination), (Get-LongPath $target))
                $displaced++
            }
        } else {
            $missing++
        }
    }

    foreach ($entry in @($manifest.backups)) {
        if ($null -eq $entry) { continue }
        if ($alreadyInPlace.ContainsKey($entry.path)) { $restored++; continue }
        $backup = Join-Path $backupRoot $entry.path
        $destination = Get-SafeDestination $Game $entry.path
        if (-not (Test-FileExists $backup)) { $incomplete++; continue }
        if ((Get-Sha256 $backup) -ne $entry.sha256) { $incomplete++; continue }
        $destinationDir = Split-Path -Parent $destination
        if (-not (Test-DirExists $destinationDir)) { [void][System.IO.Directory]::CreateDirectory((Get-LongPath $destinationDir)) }
        [System.IO.File]::Copy((Get-LongPath $backup), (Get-LongPath $destination), $true)
        if ((Get-Sha256 $destination) -ne $entry.sha256) { $incomplete++; continue }
        [System.IO.File]::Delete((Get-LongPath $backup))
        $restored++
    }

    if ($incomplete -gt 0) {
        Write-Log ("Rollback INCOMPLETE: {0} file(s) could not be restored; manifest and backups kept." -f $incomplete)
        throw "Rollback incomplete. Manifest and recoverable backups were kept."
    }

    foreach ($entry in @($manifest.files)) {
        if ($null -eq $entry) { continue }
        $directory = Split-Path -Parent (Get-SafeDestination $Game $entry.path)
        while ($directory -and (Get-NormalizedPath $directory) -ne $Game) {
            try { [System.IO.Directory]::Delete((Get-LongPath $directory), $false) } catch { break }
            $directory = Split-Path -Parent $directory
        }
    }

    [System.IO.File]::Delete((Get-LongPath $manifestPath))
    try { [System.IO.Directory]::Delete((Get-LongPath $backupRoot), $true) } catch { }
    Write-Log ("Uninstalled: removed {0}, preserved {1} edited file(s), {2} file(s) already missing, restored {3} original(s)." -f $removed, $displaced, $missing, $restored)
}


# Resolve paths, enable the log, and run the requested action.
try {
    if ($Action -eq 'Install') {
        if (-not $GamePath) { $GamePath = Find-GamePath }
        if (-not $GamePath) { $GamePath = Read-Host 'Storm 4 game folder (the one containing NSUNS4.exe)' }
        $GamePath = Get-NormalizedPath $GamePath
        if (-not (Test-FileExists (Join-Path $GamePath 'NSUNS4.exe'))) { throw "NSUNS4.exe not found in $GamePath." }
        if (-not $SourcePath) { $SourcePath = Read-Host 'Extracted pack folder (contains moddingapi)' }
        $SourcePath = Resolve-PackRoot $SourcePath
        if ($SourcePath -eq $GamePath -or
            $SourcePath.StartsWith($GamePath + '\', [System.StringComparison]::OrdinalIgnoreCase) -or
            $GamePath.StartsWith($SourcePath + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "SourcePath and GamePath overlap. Point SourcePath at the extracted pack folder, not the game folder."
        }
    } else {
        if (-not $GamePath) { $GamePath = Find-GamePath }
        if (-not $GamePath) { $GamePath = Read-Host 'Storm 4 game folder (the one containing NSUNS4.exe)' }
        $GamePath = Get-NormalizedPath $GamePath
        if (-not (Test-FileExists (Join-Path $GamePath 'NSUNS4.exe'))) { throw "NSUNS4.exe not found in $GamePath." }
    }

    if (-not $DryRun) {
        if (-not $LogPath) { $LogPath = Join-Path $env:LOCALAPPDATA 'SenjuWoo\WooPack\install.log' }
        $logDir = Split-Path -Parent $LogPath
        if (-not (Test-DirExists $logDir)) { [void][System.IO.Directory]::CreateDirectory((Get-LongPath $logDir)) }
        $script:LogPath = $LogPath
    }

    if ($Action -eq 'Install') { Install-Pack -Game $GamePath -Source $SourcePath }
    else { Uninstall-Pack -Game $GamePath }
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
