$ErrorActionPreference = 'Stop'

$backendAppPath = Join-Path (Join-Path (Join-Path $PSScriptRoot '..') 'backend') 'app'
$backendPath = Join-Path (Join-Path $PSScriptRoot '..') 'backend'
$venvPath = Join-Path $backendAppPath '.venv'
$activate = Join-Path (Join-Path $venvPath 'Scripts') 'Activate.ps1'

if (-not (Test-Path $venvPath)) {
    Write-Host "[backend] Creating virtualenv at $venvPath" -ForegroundColor Cyan
    py -m venv $venvPath
}

$req = Join-Path $backendAppPath 'requirements.txt'
if (Test-Path $req) {
    Write-Host "[backend] Installing requirements" -ForegroundColor Cyan
    & powershell -NoProfile -ExecutionPolicy Bypass -Command "& '$activate'; pip install -r '$req'"
}

Write-Host "[backend] Starting uvicorn at http://localhost:8000" -ForegroundColor Green
& powershell -NoProfile -ExecutionPolicy Bypass -Command "& '$activate'; Set-Location '$backendPath'; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
