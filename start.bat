@echo off
setlocal enabledelayedexpansion
color 0A

REM Set the working directory to the script's location
cd /d "%~dp0"

echo +--------------------------------------------------+
echo ^|  GitEvents - Start Application                   ^|
echo +--------------------------------------------------+
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    color 0E
    echo [WARNING] Virtual environment not found.
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    color 0A
    echo [OK] Virtual environment created.
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated.

REM Check if Python packages are installed
if not exist venv\Lib\site-packages\fastapi (
    color 0E
    echo [WARNING] Python packages not installed.
    echo Installing Python packages...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [ERROR] Failed to install Python packages.
        pause
        exit /b 1
    )
    color 0A
    echo [OK] Python packages installed.
)

REM Check if Node.js packages are installed
if not exist node_modules (
    color 0E
    echo [WARNING] Node.js packages not installed.
    echo Installing Node.js packages...
    npm install
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [ERROR] Failed to install Node.js packages.
        pause
        exit /b 1
    )
    color 0A
    echo [OK] Node.js packages installed.
)

REM Start backend server in a new window
echo Starting backend server...
start "GitEvents Backend" cmd /c "cd /d "%~dp0" && color 0A && echo GitEvents Backend Server && echo. && call venv\Scripts\activate.bat && python main.py"

REM Wait a moment for the backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

REM Start frontend server in a new window
echo Starting frontend server...
start "GitEvents Frontend" cmd /c "cd /d "%~dp0" && color 0B && echo GitEvents Frontend Server && echo. && npm start"

echo.
echo +--------------------------------------------------+
echo ^|  GitEvents is now running!                       ^|
echo +--------------------------------------------------+
echo.
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window. The servers will continue running.
pause > nul
