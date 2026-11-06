@echo off
setlocal
cd /d "%~dp0"
where powershell.exe >nul 2>nul || (echo Windows PowerShell was not found.& pause & exit /b 1)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_windows.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" pause
exit /b %EXIT_CODE%