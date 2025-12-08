@echo off
echo ========================================
echo NBFC Agentic AI Loan System - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18 or higher
    pause
    exit /b 1
)

echo [1/4] Installing backend dependencies...
cd backend
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
echo Backend dependencies installed

echo.
echo [2/4] Installing frontend dependencies...
cd ..\frontend
call npm install >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
echo Frontend dependencies installed

echo.
echo [3/4] Starting backend server...
cd ..\backend
start "NBFC Backend" cmd /k "python main.py"
timeout /t 3 /nobreak >nul

echo.
echo [4/4] Starting frontend server...
cd ..\frontend
start "NBFC Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo System started successfully!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul
start http://localhost:3000
echo.
echo Press any key to stop all servers...
pause >nul

REM Kill the servers
taskkill /FI "WindowTitle eq NBFC Backend*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq NBFC Frontend*" /T /F >nul 2>&1

echo.
echo Servers stopped.
pause
