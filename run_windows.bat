@echo off
echo ===================================
echo GitEvents - Windows Launcher
echo ===================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if .env file exists, if not create from example
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo .env file created. Please edit it with your configuration.
    echo.
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment and install dependencies
echo Activating virtual environment and installing Python dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

REM Start backend server in a new window
echo Starting backend server...
start cmd /k "call venv\Scripts\activate.bat && python main.py"

REM Wait a moment for the backend to start
timeout /t 5 /nobreak > nul

REM Start frontend server
echo Starting frontend server...
start cmd /k "npm start"

echo.
echo GitEvents is now running!
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window. The servers will continue running.
pause > nul
