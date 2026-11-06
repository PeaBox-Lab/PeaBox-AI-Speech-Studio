@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_worker_windows.ps1"
exit /b %ERRORLEVEL%
