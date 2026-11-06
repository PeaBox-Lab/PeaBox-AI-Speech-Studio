$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$venvPython=Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if(-not(Test-Path $venvPython)){Write-Host "Run start_windows.bat once to create the environment." -ForegroundColor Red;exit 1}
Write-Host "Starting PeaBox local worker daemon v0.11.0. Press Ctrl+C for foreground shutdown." -ForegroundColor Cyan
& $venvPython "worker_local.py" --daemon
exit $LASTEXITCODE
