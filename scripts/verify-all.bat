@echo off
setlocal
cd /d "%~dp0\.."

echo.
echo ====================================================================
echo CYBER DOPPELGANGER PHASE 1 FOUNDATION VERIFICATION
echo ====================================================================

echo.
echo [1/3] Running Python Agent Unit Tests and Health Check...
.\.venv\Scripts\python.exe -m unittest agent\tests\test_agent.py
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Python Agent unit tests failed!
    goto error
)

.\.venv\Scripts\python.exe agent\main.py --health
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Python Agent health check failed!
    goto error
)

echo.
echo [2/3] Verifying Frontend TypeScript and Vite Build...
cd frontend
call npm run build
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Frontend build failed!
    goto error
)
cd ..

echo.
echo [3/3] Verifying Spring Boot Backend...
cd backend
call .\mvnw.cmd test-compile
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Backend compilation failed!
    goto error
)
cd ..

echo.
echo ====================================================================
echo [PASS] ALL PHASE 1 FOUNDATION VERIFICATIONS COMPLETED SUCCESSFULLY
echo ====================================================================
echo.
pause
exit /b 0

:error
echo.
echo [ERROR] Verification failed.
pause
exit /b 1
