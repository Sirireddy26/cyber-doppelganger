# ====================================================================
# Cyber Doppelganger - Phase 1 Foundation Verification Runner
# ====================================================================

Write-Host ""
Write-Host "=== CYBER DOPPELGANGER PHASE 1 FOUNDATION VERIFICATION ===" -ForegroundColor Cyan

$projectRoot = Join-Path $PSScriptRoot ".."
$agentPy = Join-Path $projectRoot ".venv\Scripts\python.exe"

# 1. Verify Python Agent Unit Tests & Health
Write-Host ""
Write-Host "[1/3] Running Python Agent Unit Tests & Diagnostics..." -ForegroundColor Yellow
if (Test-Path $agentPy) {
    Push-Location $projectRoot
    & $agentPy -m unittest discover -s "agent\tests" -p "test_*.py"
    $unitTestExit = $LASTEXITCODE
    Pop-Location

    if ($unitTestExit -ne 0) {
        Write-Host "[FAIL] Python Agent unit tests failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[PASS] Python Agent unit tests passed." -ForegroundColor Green

    Write-Host ""
    Write-Host "Running Agent CLI Health Check:" -ForegroundColor Yellow
    Push-Location $projectRoot
    & $agentPy "agent\main.py" --health
    $healthExit = $LASTEXITCODE
    Pop-Location

    if ($healthExit -ne 0) {
        Write-Host "[FAIL] Python Agent health check failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[PASS] Python Agent health check verified." -ForegroundColor Green
} else {
    Write-Host "[FAIL] Virtual environment Python not found at: $agentPy" -ForegroundColor Red
    exit 1
}

# 2. Verify Frontend Build (TypeScript & Vite)
Write-Host ""
Write-Host "[2/3] Verifying Frontend TypeScript & Vite Production Build..." -ForegroundColor Yellow
$frontendDir = Join-Path $projectRoot "frontend"
Push-Location $frontendDir
npm run build
$buildExit = $LASTEXITCODE
Pop-Location

if ($buildExit -ne 0) {
    Write-Host "[FAIL] Frontend build failed!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "[PASS] Frontend built successfully without errors." -ForegroundColor Green
}

# 3. Verify Backend Compilation
Write-Host ""
Write-Host "[3/3] Verifying Spring Boot Backend Context & Compilation..." -ForegroundColor Yellow
$backendDir = Join-Path $projectRoot "backend"
Push-Location $backendDir
.\mvnw.cmd test-compile
$backendExit = $LASTEXITCODE
Pop-Location

if ($backendExit -ne 0) {
    Write-Host "[FAIL] Backend compilation failed!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "[PASS] Spring Boot Backend compiled successfully." -ForegroundColor Green
}

Write-Host ""
Write-Host "=== ALL PHASE 1 FOUNDATION VERIFICATIONS COMPLETED SUCCESSFULLY ===" -ForegroundColor Cyan
Write-Host ""
