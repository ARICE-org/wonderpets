$ErrorActionPreference = 'Stop'

$frontendPath = Join-Path $PSScriptRoot '..' 'frontend'

if (-not (Test-Path (Join-Path $frontendPath 'node_modules'))) {
    Write-Host "[frontend] Installing npm dependencies" -ForegroundColor Cyan
    Push-Location $frontendPath
    try {
        npm install
    } finally { Pop-Location }
}

Write-Host "[frontend] Starting Expo (press 'w' in that window to open web, or scan QR for device)" -ForegroundColor Green
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-ExecutionPolicy","Bypass","-Command", "Set-Location '$frontendPath'; npx expo start" | Out-Null
