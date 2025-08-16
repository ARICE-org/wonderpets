param(
    [switch]$NoInstall
)

$ErrorActionPreference = 'Stop'

function Ensure-Backend-Venv {
    $backendAppPath = Join-Path (Join-Path (Join-Path $PSScriptRoot '..') 'backend') 'app'
    $venvPath = Join-Path $backendAppPath '.venv'
    $activate = Join-Path (Join-Path $venvPath 'Scripts') 'Activate.ps1'
    if (-not (Test-Path $venvPath)) {
        Write-Host "[backend] Creating virtualenv at $venvPath" -ForegroundColor Cyan
        py -m venv $venvPath
    }
    if (-not $NoInstall) {
        $req = Join-Path $backendAppPath 'requirements.txt'
        if (Test-Path $req) {
            Write-Host "[backend] Installing requirements" -ForegroundColor Cyan
            & powershell -NoProfile -ExecutionPolicy Bypass -Command "& '$activate'; pip install -r '$req'"
        }
    }
}

function Start-Backend {
    $backendPath = Join-Path (Join-Path $PSScriptRoot '..') 'backend'
    $backendAppPath = Join-Path (Join-Path (Join-Path $PSScriptRoot '..') 'backend') 'app'
    $activate = Join-Path (Join-Path (Join-Path $backendAppPath '.venv') 'Scripts') 'Activate.ps1'
    $cmd = "& '$activate'; Set-Location '$backendPath'; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir 'app' --reload-include '*.py' --reload-exclude '*.db' --reload-exclude '.venv/*'"
    Write-Host "[backend] Starting uvicorn at http://localhost:8000" -ForegroundColor Green
    Start-Process -FilePath "powershell" -ArgumentList "-ExecutionPolicy","Bypass","-Command", $cmd | Out-Null
}

function Ensure-Frontend-Deps {
    $frontendPath = Join-Path (Join-Path $PSScriptRoot '..') 'frontend'
    $nodeModules = Join-Path $frontendPath 'node_modules'
    if (-not $NoInstall -and -not (Test-Path $nodeModules)) {
        Write-Host "[frontend] Installing npm dependencies" -ForegroundColor Cyan
        Push-Location $frontendPath
        try {
            npm install
        } finally { Pop-Location }
    }
}

function Start-Frontend {
    $frontendPath = Join-Path (Join-Path $PSScriptRoot '..') 'frontend'
    $cmd = "Set-Location '$frontendPath'; npx expo start"
    Write-Host "[frontend] Starting Expo (press 'w' in that window to open web, or scan QR for device)" -ForegroundColor Green
    Start-Process -FilePath "powershell" -ArgumentList "-ExecutionPolicy","Bypass","-Command", $cmd | Out-Null
}

# Run
Ensure-Backend-Venv
Ensure-Frontend-Deps
Start-Backend
Start-Frontend

Write-Host "\nDev scripts launched in separate terminals." -ForegroundColor Yellow
Write-Host "Backend: http://localhost:8000  |  Frontend: Expo Dev Server (http://localhost:8081 by default)" -ForegroundColor Yellow
