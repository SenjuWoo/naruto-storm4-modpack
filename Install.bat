@echo off
rem Transactional installer for the Woo Storm 4 pack.
rem It backs up replaced files and records SHA-256 hashes; see scripts\WooPack.ps1.
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\WooPack.ps1" -Action Install %*
if errorlevel 1 pause
endlocal
