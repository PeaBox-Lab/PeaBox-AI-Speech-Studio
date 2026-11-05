$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$MinimumVersion = [Version]"3.10.0"
$MaximumVersion = [Version]"3.13.0"

function Get-CompatibleVersion {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [string[]]$PrefixArguments = @()
    )

    try {
        $versionText = & $Executable @PrefixArguments -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $versionText) { return $null }
        $version = [Version]($versionText | Select-Object -Last 1)
        if ($version -ge $MinimumVersion -and $version -lt $MaximumVersion) { return $version }
    }
    catch { return $null }
    return $null
}

function Find-CompatiblePython {
    $candidates = @(
        @{ Name = "Python 3.12 via Python Launcher"; Executable = "py"; Arguments = @("-3.12") },
        @{ Name = "Python 3.11 via Python Launcher"; Executable = "py"; Arguments = @("-3.11") },
        @{ Name = "Python 3.10 via Python Launcher"; Executable = "py"; Arguments = @("-3.10") },
        @{ Name = "python command"; Executable = "python"; Arguments = @() },
        @{ Name = "python3 command"; Executable = "python3"; Arguments = @() }
    )

    foreach ($candidate in $candidates) {
        if (-not (Get-Command $candidate.Executable -ErrorAction SilentlyContinue)) { continue }
        $version = Get-CompatibleVersion -Executable $candidate.Executable -PrefixArguments $candidate.Arguments
        if ($null -ne $version) {
            return @{
                Name = $candidate.Name
                Executable = $candidate.Executable
                Arguments = $candidate.Arguments
                Version = $version
            }
        }
    }
    return $null
}

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $venvVersion = Get-CompatibleVersion -Executable $venvPython
    if ($null -ne $venvVersion) {
        Write-Host "Using existing virtual environment with Python $venvVersion." -ForegroundColor Green
    }
    else {
        Write-Warning "The existing .venv is incomplete or uses an unsupported Python version. Rebuilding it."
        Remove-Item -Recurse -Force (Join-Path $PSScriptRoot ".venv")
    }
}

if (-not (Test-Path $venvPython)) {
    $python = Find-CompatiblePython
    if ($null -eq $python) {
        Write-Host "No compatible Python installation was found." -ForegroundColor Red
        Write-Host "Install 64-bit Python 3.10, 3.11, or 3.12, then run start_windows.bat again."
        Write-Host "During installation, enable the Python Launcher or add Python to PATH."
        exit 1
    }

    Write-Host "Found $($python.Name): Python $($python.Version)." -ForegroundColor Green
    Write-Host "Creating the virtual environment..."
    $pythonArguments = @($python.Arguments)
    & $python.Executable @pythonArguments -m venv ".venv"
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $venvPython)) {
        Write-Host "Python was found, but the virtual environment could not be created." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Preparing PeaBox Voice Studio..."
& $venvPython -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $venvPython -m pip install -r "requirements.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Starting PeaBox Voice Studio..." -ForegroundColor Green
& $venvPython -m streamlit run "app.py"
exit $LASTEXITCODE
