# load-venv-env.ps1
# This script loads environment variables from a .env file

$envFilePath = ".\.env"

if (Test-Path $envFilePath) {
    Get-Content $envFilePath | ForEach-Object {
        # Skip empty lines and comments
        if ($_ -and ($_ -notmatch '^\s*#')) {
            $parts = $_ -split '=', 2
            if ($parts.Length -eq 2) {
                $name = $parts[0].Trim()
                $value = $parts[1].Trim()
                # Use ${} for dynamic env variable names
                Set-Item -Path "Env:$name" -Value $value
                Write-Host "Set $name=$value"
            }
        }
    }
    Write-Host "All environment variables loaded from .env"
} else {
    Write-Host ".env file not found at $envFilePath" -ForegroundColor Red
}
