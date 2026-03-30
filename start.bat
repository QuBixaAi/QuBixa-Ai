@echo off
echo ========================================
echo QUBIXA AI - Starting Platform
echo ========================================

echo.
echo [1/3] Checking setup...
python test_setup.py

echo.
echo [2/3] Starting Backend Server...
echo Backend will run on http://localhost:8000
echo.
start "Qubixa Backend" cmd /k "python main.py"

timeout /t 3 /nobreak >nul

echo.
echo [3/3] Starting Frontend...
echo Frontend will run on http://localhost:3000
echo.
cd web
start "Qubixa Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo QUBIXA AI Platform Started!
echo ========================================
echo.
echo Dashboard: http://localhost:3000
echo API Docs:  http://localhost:8000/docs
echo.
echo Press any key to exit this window...
pause >nul
