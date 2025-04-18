@echo off
echo ===================================
echo GitEvents - Windows Launcher
echo ===================================
echo.

REM Set error handling
setlocal enabledelayedexpansion

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check Python version
python -c "import sys; print(sys.version_info.major, sys.version_info.minor)" > temp_version.txt
set /p PYTHON_VERSION=<temp_version.txt
del temp_version.txt
for /f "tokens=1,2" %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)
if %PYTHON_MAJOR% LSS 3 (
    echo [ERROR] Python version 3.6+ is required, but found version %PYTHON_MAJOR%.%PYTHON_MINOR%
    echo Please install a newer version of Python.
    pause
    exit /b 1
)
if %PYTHON_MAJOR% EQU 3 (
    if %PYTHON_MINOR% LSS 6 (
        echo [ERROR] Python version 3.6+ is required, but found version %PYTHON_MAJOR%.%PYTHON_MINOR%
        echo Please install a newer version of Python.
        pause
        exit /b 1
    )
)
echo [OK] Python %PYTHON_MAJOR%.%PYTHON_MINOR% detected.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check Node.js version
node -v > temp_version.txt
set /p NODE_VERSION=<temp_version.txt
del temp_version.txt
echo [OK] Node.js %NODE_VERSION% detected.

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm is not installed or not in PATH.
    echo Please reinstall Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] npm detected.

REM Check if .env file exists, if not create from example
if not exist .env (
    if exist .env.example (
        echo Creating .env file from .env.example...
        copy .env.example .env
        echo [OK] .env file created. Please edit it with your configuration.
        echo.
    ) else (
        echo Creating default .env file...
        echo # GitEvents Environment Configuration > .env
        echo GITHUB_WEBHOOK_SECRET=your_webhook_secret_here >> .env
        echo GITHUB_API_TOKEN=your_github_token_here >> .env
        echo GITHUB_EVENTS_DB=github_events.db >> .env
        echo API_PORT=8001 >> .env
        echo [OK] Default .env file created. Please edit it with your configuration.
        echo.
    )
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        echo Please check your Python installation.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
    echo.
)

REM Activate virtual environment and install dependencies
echo Activating virtual environment and installing Python dependencies...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Install Python dependencies with error handling
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some Python dependencies failed to install.
    echo The application may not function correctly.
    echo.
    choice /C YN /M "Do you want to continue anyway?"
    if !ERRORLEVEL! EQU 2 (
        echo Installation aborted by user.
        pause
        exit /b 1
    )
)

REM Install Node.js dependencies with error handling
echo Installing Node.js dependencies...
npm install
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some Node.js dependencies failed to install.
    echo The frontend may not function correctly.
    echo.
    choice /C YN /M "Do you want to continue anyway?"
    if !ERRORLEVEL! EQU 2 (
        echo Installation aborted by user.
        pause
        exit /b 1
    )
)

REM Create data directory if it doesn't exist
if not exist data (
    mkdir data
    echo [OK] Created data directory.
)

REM Check if database exists, if not create it
if not exist github_events.db (
    echo Initializing database...
    python -c "from db.db_manager import DatabaseManager; DatabaseManager('github_events.db').initialize_database()"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to initialize database.
        pause
        exit /b 1
    )
    echo [OK] Database initialized.
)

REM Start backend server in a new window
echo Starting backend server...
start "GitEvents Backend" cmd /k "color 0A && echo GitEvents Backend Server && echo. && call venv\Scripts\activate.bat && python main.py"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start backend server.
    pause
    exit /b 1
)

REM Wait a moment for the backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

REM Start frontend server
echo Starting frontend server...
start "GitEvents Frontend" cmd /k "color 0B && echo GitEvents Frontend Server && echo. && npm start"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start frontend server.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] GitEvents is now running!
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window. The servers will continue running.
pause > nul
