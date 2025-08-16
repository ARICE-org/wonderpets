$ErrorActionPreference = 'Stop'

function Get-PIDsByPort {
    param(
        [Parameter(Mandatory=$true)][int]$Port
    )
    $pids = @()
    try {
        # Prefer Get-NetTCPConnection when available
        if (Get-Command Get-NetTCPConnection -ErrorAction SilentlyContinue) {
            $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
            if ($conns) {
                $pids += ($conns | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique)
            }
        } else {
            throw 'Get-NetTCPConnection not available'
        }
    } catch {
        # Fallback to netstat parsing
        $lines = netstat -ano | Select-String ":$Port" | ForEach-Object { $_.ToString() }
        foreach ($line in $lines) {
            if ($line -match "LISTENING\s+(\d+)$") {
                $pids += [int]$Matches[1]
            }
        }
        $pids = $pids | Sort-Object -Unique
    }
    return $pids
}

function Stop-ByPort {
    param([int]$Port)
    $getPids = Get-PIDsByPort -Port $Port
    if ($getPids -and $getPids.Count -gt 0) {
        Write-Host "Stopping processes on port ${Port} : $($getPids -join ', ')" -ForegroundColor Yellow
        foreach ($pids in $getPids) {
            try { Stop-Process -Id $pids -Force -ErrorAction Stop } catch { }
        }
    } else {
        Write-Host "No listeners found on port ${Port}: " -ForegroundColor DarkGray
    }
}

function Stop-ByCommandLine {
    param(
        [Parameter(Mandatory=$true)][string]$Pattern,
        [string]$Label = $null
    )
    $labelText = if ($Label) { $Label } else { $Pattern }
    try {
        $procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -match $Pattern }
        if ($procs) {
            $ids = $procs.ProcessId
            Write-Host "Stopping processes by pattern [$labelText]: $($ids -join ', ')" -ForegroundColor Yellow
            foreach ($id in $ids) {
                try { Stop-Process -Id $id -Force -ErrorAction Stop } catch { }
            }
        } else {
            Write-Host "No processes matched pattern [$labelText]" -ForegroundColor DarkGray
        }
    } catch {
        Write-Host "Process query failed for pattern [$labelText]: $_" -ForegroundColor Red
    }
}

Write-Host "Stopping dev environment (backend + frontend)..." -ForegroundColor Cyan

# Common dev ports
$ports = @(8000, 8081, 19000, 19001, 19002)
foreach ($p in $ports) { Stop-ByPort -Port $p }

# Match backend uvicorn and frontend expo processes by command line
Stop-ByCommandLine -Pattern 'uvicorn\s+app\.main:app' -Label 'FastAPI uvicorn'
Stop-ByCommandLine -Pattern 'expo(\.cmd)?\s+start' -Label 'Expo CLI'
Stop-ByCommandLine -Pattern 'node.+@expo/cli' -Label 'Expo Node'

Write-Host "Done. If any windows remain open, you can close them manually; the underlying processes should be terminated." -ForegroundColor Green
