param(
    [int]$WindowSeconds = 15
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Cyber Doppelganger Behavioural Agent (Phase 2)" -ForegroundColor Cyan
Write-Host "Aggregation Window: $WindowSeconds seconds" -ForegroundColor Gray
Write-Host "Storage: agent/data/feature_snapshots.jsonl" -ForegroundColor Gray
Write-Host "Press Ctrl+C at any time to stop cleanly." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

& ".\.venv\Scripts\python.exe" "agent\main.py" --window-seconds $WindowSeconds
