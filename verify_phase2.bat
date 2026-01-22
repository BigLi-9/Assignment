@echo off
echo ====================================
echo Phase 2 - Final Verification Test
echo ====================================
echo.

cd /d "C:\Users\78785\Desktop\Assignment"

echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 2: Starting FastAPI server in background...
start /B python run.py
timeout /t 5 /nobreak > nul

echo.
echo Step 3: Testing /health endpoint...
curl -s http://localhost:8000/health

echo.
echo.
echo Step 4: Testing /analyze endpoint (this takes 5-10 seconds)...
python test_analyze.py

echo.
echo ====================================
echo Phase 2 Verification Complete!
echo ====================================
pause
