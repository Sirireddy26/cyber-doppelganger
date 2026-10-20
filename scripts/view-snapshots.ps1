$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$SnapshotFile = "agent/data/feature_snapshots.jsonl"

if (-not (Test-Path $SnapshotFile)) {
    Write-Host "No feature snapshots found yet at $SnapshotFile" -ForegroundColor Yellow
    Write-Host "Run .\scripts\run-agent.ps1 first to record behavioural windows." -ForegroundColor Gray
    exit 0
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Cyber Doppelganger - Behavioural Feature Snapshots" -ForegroundColor Cyan
Write-Host "File: $SnapshotFile" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Cyan

& ".\.venv\Scripts\python.exe" -c @"
import json
from pathlib import Path

p = Path('$SnapshotFile')
if p.exists():
    lines = [l.strip() for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
    print(f'Total Snapshots Recorded: {len(lines)}')
    if lines:
        print('\n--- LATEST FEATURE SNAPSHOT (PRETTY PRINT) ---')
        latest = json.loads(lines[-1])
        print(json.dumps(latest, indent=2))
"@
