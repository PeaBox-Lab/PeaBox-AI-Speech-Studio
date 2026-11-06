$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$MinimumVersion = [Version]"3.10.0"
$MaximumVersion = [Version]"3.13.0"
function Get-CompatibleVersion { param([string]$Executable,[string[]]$PrefixArguments=@()) try { $v=& $Executable @PrefixArguments -c "import sys; print('.'.join(map(str,sys.version_info[:3])))" 2>$null; if($LASTEXITCODE -eq 0 -and $v){$x=[Version]($v|Select-Object -Last 1);if($x-ge $MinimumVersion -and $x-lt $MaximumVersion){return $x}} } catch{} return $null }
function Find-CompatiblePython { $items=@(@{E="py";A=@("-3.12");N="Python 3.12"},@{E="py";A=@("-3.11");N="Python 3.11"},@{E="py";A=@("-3.10");N="Python 3.10"},@{E="python";A=@();N="python command"},@{E="python3";A=@();N="python3 command"});foreach($i in $items){if(Get-Command $i.E -ErrorAction SilentlyContinue){$v=Get-CompatibleVersion $i.E $i.A;if($null-ne $v){return @{Executable=$i.E;Arguments=$i.A;Name=$i.N;Version=$v}}}}return $null }
$venvPython=Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if(Test-Path $venvPython){$v=Get-CompatibleVersion $venvPython;if($null-eq $v){Write-Warning "Rebuilding incompatible .venv";Remove-Item -Recurse -Force ".venv"}}
if(-not(Test-Path $venvPython)){$p=Find-CompatiblePython;if($null-eq $p){Write-Host "Install 64-bit Python 3.10, 3.11, or 3.12." -ForegroundColor Red;exit 1};Write-Host "Using $($p.Name) $($p.Version)" -ForegroundColor Green;$args=@($p.Arguments);& $p.Executable @args -m venv ".venv";if($LASTEXITCODE-ne 0){exit $LASTEXITCODE}}
& $venvPython -m pip install --upgrade pip setuptools wheel
if($LASTEXITCODE-ne 0){exit $LASTEXITCODE}
& $venvPython -m pip install -r "requirements.txt" -c "constraints.txt"
if($LASTEXITCODE-ne 0){exit $LASTEXITCODE}
Write-Host "Launching PeaBox Voice Studio v0.10.9 from $PSScriptRoot" -ForegroundColor Cyan
& $venvPython -m streamlit run "app.py"
exit $LASTEXITCODE
