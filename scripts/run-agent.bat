@echo off
cd /d "%~dp0\.."
echo ============================================================
echo Starting Cyber Doppelganger Behavioural Agent (Phase 2)
echo Press Ctrl+C at any time to stop cleanly.
echo ============================================================
.\.venv\Scripts\python.exe agent\main.py --window-seconds 15 %*
pause
