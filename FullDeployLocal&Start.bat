@echo off
setlocal enabledelayedexpansion
color 0A

echo ===================================
echo GitEvents - Full Deploy & Start
echo ===================================
echo.

REM Set error handling
set ERROR_COUNT=0
set WARNING_COUNT=0

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    color 0C
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
    color 0C
    echo [ERROR] Python version 3.6+ is required, but found version %PYTHON_MAJOR%.%PYTHON_MINOR%
    echo Please install a newer version of Python.
    pause
    exit /b 1
)
if %PYTHON_MAJOR% EQU 3 (
    if %PYTHON_MINOR% LSS 6 (
        color 0C
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
    color 0C
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
    color 0C
    echo [ERROR] npm is not installed or not in PATH.
    echo Please reinstall Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] npm detected.

REM Check if Git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Git is not installed or not in PATH.
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)
echo [OK] Git detected.

REM Check if we're in a git repository
if not exist .git (
    color 0C
    echo [ERROR] Not in a Git repository. Please run this script from the GitEvents directory.
    pause
    exit /b 1
)

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

REM Create data directory if it doesn't exist
if not exist data (
    mkdir data
    echo [OK] Created data directory.
)

REM Create Python virtual environment
echo Creating Python virtual environment...
if exist venv (
    echo [INFO] Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [ERROR] Failed to create virtual environment.
        echo Please check your Python installation.
        set /a ERROR_COUNT+=1
    ) else (
        echo [OK] Virtual environment created.
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to activate virtual environment.
    set /a ERROR_COUNT+=1
) else (
    echo [OK] Virtual environment activated.
)

REM Install Python dependencies with retry mechanism
echo Installing Python dependencies...
set RETRY_COUNT=0
:RETRY_PIP
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    set /a RETRY_COUNT+=1
    if %RETRY_COUNT% LSS 3 (
        echo [WARNING] Failed to install some Python dependencies. Retrying... (Attempt %RETRY_COUNT% of 3)
        timeout /t 3 /nobreak > nul
        goto RETRY_PIP
    ) else (
        color 0E
        echo [WARNING] Some Python dependencies failed to install after 3 attempts.
        echo The application may not function correctly.
        set /a WARNING_COUNT+=1
    )
) else (
    echo [OK] Python dependencies installed successfully.
)

REM Install Node.js dependencies with retry mechanism
echo Installing Node.js dependencies...
set RETRY_COUNT=0
:RETRY_NPM
call npm install
if %ERRORLEVEL% NEQ 0 (
    set /a RETRY_COUNT+=1
    if %RETRY_COUNT% LSS 3 (
        echo [WARNING] Failed to install some Node.js dependencies. Retrying... (Attempt %RETRY_COUNT% of 3)
        timeout /t 3 /nobreak > nul
        goto RETRY_NPM
    ) else (
        color 0E
        echo [WARNING] Some Node.js dependencies failed to install after 3 attempts.
        echo The frontend may not function correctly.
        set /a WARNING_COUNT+=1
    )
) else (
    echo [OK] Node.js dependencies installed successfully.
)

REM Fix npm vulnerabilities
echo Fixing npm vulnerabilities...
call npm audit fix --force
if %ERRORLEVEL% NEQ 0 (
    color 0E
    echo [WARNING] Could not fix all npm vulnerabilities.
    echo The application may have security issues.
    set /a WARNING_COUNT+=1
) else (
    echo [OK] npm vulnerabilities fixed.
)

REM Check if database exists, if not create it
if not exist github_events.db (
    echo Initializing database...
    python -c "from db.db_manager import DatabaseManager; db = DatabaseManager('github_events.db'); db.initialize_database()"
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [ERROR] Failed to initialize database.
        set /a ERROR_COUNT+=1
    ) else (
        echo [OK] Database initialized.
    )
)

REM Check if there are any errors
if %ERROR_COUNT% GTR 0 (
    color 0C
    echo.
    echo [CRITICAL] There were %ERROR_COUNT% errors during deployment.
    echo Please fix these errors before continuing.
    echo.
    pause
    exit /b 1
)

REM Check if there are any warnings
if %WARNING_COUNT% GTR 0 (
    color 0E
    echo.
    echo [WARNING] There were %WARNING_COUNT% warnings during deployment.
    echo The application may not function correctly.
    echo.
    choice /C YN /M "Do you want to continue anyway?"
    if !ERRORLEVEL! EQU 2 (
        echo Deployment aborted by user.
        pause
        exit /b 1
    )
)

REM Start backend server in a new window
echo Starting backend server...
start "GitEvents Backend" cmd /k "color 0A && echo GitEvents Backend Server && echo. && call venv\Scripts\activate.bat && python main.py"
if %ERRORLEVEL% NEQ 0 (
    color 0C
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
    color 0C
    echo [ERROR] Failed to start frontend server.
    pause
    exit /b 1
)

color 0A
echo.
echo ===================================
echo GitEvents Deployment Complete!
echo ===================================
echo.
echo [SUCCESS] GitEvents is now running!
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window. The servers will continue running.
pause > nul
