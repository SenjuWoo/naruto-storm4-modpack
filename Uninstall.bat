@echo off
rem Transactional uninstaller for the Woo Storm 4 pack.
rem It restores backed-up files and preserves post-install edits; see scripts\WooPack.ps1.
setlocal
if not exist "%~dp0scripts\WooPack.ps1" (
    echo Missing scripts\WooPack.ps1. Download the repository ZIP, or keep the scripts folder beside Uninstall.bat.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\WooPack.ps1" -Action Uninstall %*
if errorlevel 1 pause
endlocal
