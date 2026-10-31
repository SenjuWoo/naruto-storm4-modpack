@echo off
rem Transactional uninstaller for the Woo Storm 4 pack.
rem It restores backed-up files and preserves post-install edits; see scripts\WooPack.ps1.
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\WooPack.ps1" -Action Uninstall %*
if errorlevel 1 pause
endlocal
