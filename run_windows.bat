@echo off
setlocal enabledelayedexpansion

:: Set color codes for better visibility
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "RESET=[0m"

echo %CYAN%╔════════════════════════════════════════════╗%RESET%
echo %CYAN%║  GitEvents - Windows Launcher               ║%RESET%
echo %CYAN%╚════════════════════════════════════════════╝%RESET%
echo.

:: Check if running as administrator
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%Note: Some features may require administrator privileges.%RESET%
    echo %YELLOW%If you encounter permission issues, try running as administrator.%RESET%
    echo.
)

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Python is not installed or not in PATH.%RESET%
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Check Python version
python -c "import sys; print(sys.version_info.major, sys.version_info.minor)" > temp_version.txt
set /p PYTHON_VERSION=<temp_version.txt
del temp_version.txt
for /f "tokens=1,2" %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)
if %PYTHON_MAJOR% LSS 3 (
    echo %RED%[ERROR] Python version 3.6+ is required, but found version %PYTHON_MAJOR%.%PYTHON_MINOR%%RESET%
    echo Please install a newer version of Python.
    pause
    exit /b 1
)
if %PYTHON_MAJOR% EQU 3 (
    if %PYTHON_MINOR% LSS 6 (
        echo %RED%[ERROR] Python version 3.6+ is required, but found version %PYTHON_MAJOR%.%PYTHON_MINOR%%RESET%
        echo Please install a newer version of Python.
        pause
        exit /b 1
    )
)
echo %GREEN%[OK] Python %PYTHON_MAJOR%.%PYTHON_MINOR% detected.%RESET%

:: Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Node.js is not installed or not in PATH.%RESET%
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

:: Check Node.js version
node -v > temp_version.txt
set /p NODE_VERSION=<temp_version.txt
del temp_version.txt
echo %GREEN%[OK] Node.js %NODE_VERSION% detected.%RESET%

:: Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] npm is not installed or not in PATH.%RESET%
    echo Please reinstall Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo %GREEN%[OK] npm detected.%RESET%

:: Check if .env file exists, if not create from example
if not exist .env (
    if exist .env.example (
        echo Creating .env file from .env.example...
        copy .env.example .env
        echo %GREEN%[OK] .env file created. Please edit it with your configuration.%RESET%
        echo.
    ) else (
        echo Creating default .env file...
        echo # GitEvents Environment Configuration > .env
        echo GITHUB_WEBHOOK_SECRET=your_webhook_secret_here >> .env
        echo GITHUB_API_TOKEN=your_github_token_here >> .env
        echo GITHUB_EVENTS_DB=github_events.db >> .env
        echo API_PORT=8001 >> .env
        echo DB_TYPE=sqlite >> .env
        echo %GREEN%[OK] Default .env file created. Please edit it with your configuration.%RESET%
        echo.
    )
)

:: Check if virtual environment exists
if not exist venv (
    echo %CYAN%Creating Python virtual environment...%RESET%
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo %RED%[ERROR] Failed to create virtual environment.%RESET%
        echo Please check your Python installation.
        
        :: Try to diagnose the issue
        echo.
        echo %YELLOW%Attempting to diagnose the issue...%RESET%
        python -c "import ensurepip; print('ensurepip module:', 'available' if ensurepip else 'not available')"
        
        pause
        exit /b 1
    )
    echo %GREEN%[OK] Virtual environment created.%RESET%
    echo.
)

:: Activate virtual environment and install dependencies
echo %CYAN%Activating virtual environment and installing Python dependencies...%RESET%
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Failed to activate virtual environment.%RESET%
    
    :: Try to diagnose the issue
    echo.
    echo %YELLOW%Attempting to diagnose the issue...%RESET%
    if not exist venv\Scripts\activate.bat (
        echo %RED%Virtual environment activation script not found.%RESET%
        echo Attempting to recreate the virtual environment...
        rmdir /s /q venv
        python -m venv venv
        if %ERRORLEVEL% EQU 0 (
            call venv\Scripts\activate.bat
            if %ERRORLEVEL% NEQ 0 (
                echo %RED%Still unable to activate virtual environment.%RESET%
                pause
                exit /b 1
            )
        ) else (
            echo %RED%Failed to recreate virtual environment.%RESET%
            pause
            exit /b 1
        )
    ) else (
        pause
        exit /b 1
    )
)

:: Check if requirements.txt exists
if not exist requirements.txt (
    echo %YELLOW%[WARNING] requirements.txt not found. Creating default file...%RESET%
    (
        echo # API and Web Framework
        echo fastapi>=0.95.0
        echo uvicorn>=0.21.1
        echo python-dotenv>=1.0.0
        echo pydantic>=2.0.0
        echo starlette>=0.27.0
        echo.
        echo # Database
        echo sqlalchemy>=2.0.0
        echo pymysql>=1.0.3  # MySQL support
        echo cryptography>=41.0.0  # Required for PyMySQL on Windows
        echo.
        echo # GitHub Integration
        echo PyGithub>=1.58.0
        echo pyjwt>=2.6.0
        echo.
        echo # Webhook Handling
        echo python-multipart>=0.0.6
        echo httpx>=0.24.0
        echo.
        echo # Ngrok for Tunneling
        echo pyngrok>=6.0.0
        echo.
        echo # Utilities
        echo python-dateutil>=2.8.2
        echo pytz>=2023.3
        echo colorama>=0.4.6  # Better console output on Windows
        echo.
        echo # Windows-specific
        echo pywin32>=306; sys_platform == 'win32'  # Windows API access
        echo pyreadline3>=3.4.1; sys_platform == 'win32'  # Readline for Windows
    ) > requirements.txt
    echo %GREEN%[OK] Created default requirements.txt%RESET%
)

:: Install Python dependencies with error handling and retry mechanism
set MAX_RETRIES=3
set RETRY_COUNT=0

:install_python_deps
set /a RETRY_COUNT+=1
echo %CYAN%Installing Python dependencies (Attempt %RETRY_COUNT% of %MAX_RETRIES%)...%RESET%
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    if %RETRY_COUNT% LSS %MAX_RETRIES% (
        echo %YELLOW%[WARNING] Some Python dependencies failed to install. Retrying...%RESET%
        timeout /t 3 /nobreak > nul
        goto install_python_deps
    ) else (
        echo %RED%[WARNING] Failed to install some Python dependencies after %MAX_RETRIES% attempts.%RESET%
        echo The application may not function correctly.
        echo.
        choice /C YN /M "Do you want to continue anyway?"
        if !ERRORLEVEL! EQU 2 (
            echo Installation aborted by user.
            pause
            exit /b 1
        )
    )
) else (
    echo %GREEN%[OK] Python dependencies installed successfully.%RESET%
)

:: Install Node.js dependencies with error handling and retry mechanism
set RETRY_COUNT=0

:install_node_deps
set /a RETRY_COUNT+=1
echo %CYAN%Installing Node.js dependencies (Attempt %RETRY_COUNT% of %MAX_RETRIES%)...%RESET%
npm install
if %ERRORLEVEL% NEQ 0 (
    if %RETRY_COUNT% LSS %MAX_RETRIES% (
        echo %YELLOW%[WARNING] Some Node.js dependencies failed to install. Retrying...%RESET%
        timeout /t 3 /nobreak > nul
        goto install_node_deps
    ) else (
        echo %RED%[WARNING] Failed to install some Node.js dependencies after %MAX_RETRIES% attempts.%RESET%
        echo The frontend may not function correctly.
        echo.
        choice /C YN /M "Do you want to continue anyway?"
        if !ERRORLEVEL! EQU 2 (
            echo Installation aborted by user.
            pause
            exit /b 1
        )
    )
) else (
    echo %GREEN%[OK] Node.js dependencies installed successfully.%RESET%
)

:: Fix npm vulnerabilities automatically
echo %CYAN%Checking for npm vulnerabilities...%RESET%
npm audit fix
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%[WARNING] Some vulnerabilities could not be fixed automatically.%RESET%
    echo You may want to run 'npm audit fix --force' manually.
) else (
    echo %GREEN%[OK] npm vulnerabilities fixed.%RESET%
)

:: Create data directory if it doesn't exist
if not exist data (
    mkdir data
    echo %GREEN%[OK] Created data directory.%RESET%
)

:: Check if database exists, if not create it
if not exist github_events.db (
    echo %CYAN%Initializing database...%RESET%
    python -c "from db.db_manager import DatabaseManager; DatabaseManager('github_events.db').initialize_database()"
    if %ERRORLEVEL% NEQ 0 (
        echo %RED%[ERROR] Failed to initialize database.%RESET%
        echo Attempting to diagnose the issue...
        
        :: Check if db_manager.py exists
        if not exist db\db_manager.py (
            echo %RED%db_manager.py not found. Project structure may be incorrect.%RESET%
        ) else (
            :: Try to run with more detailed error output
            python -c "from db.db_manager import DatabaseManager; print('Imported DatabaseManager'); db = DatabaseManager('github_events.db'); print('Created DatabaseManager instance'); db.initialize_database(); print('Database initialized')"
        )
        
        pause
        exit /b 1
    )
    echo %GREEN%[OK] Database initialized.%RESET%
)

:: Create src directory and index.js if they don't exist
if not exist src (
    mkdir src
    echo %GREEN%[OK] Created src directory.%RESET%
)

if not exist src\index.js (
    echo %CYAN%Creating default src\index.js file...%RESET%
    (
        echo import React from 'react';
        echo import ReactDOM from 'react-dom/client';
        echo import './index.css';
        echo import GitHubEventsDashboard from '../dashboard/GitHubEventsDashboard';
        echo.
        echo const root = ReactDOM.createRoot(document.getElementById('root'^)^);
        echo root.render(
        echo   ^<React.StrictMode^>
        echo     ^<GitHubEventsDashboard /^>
        echo   ^</React.StrictMode^>
        echo ^);
    ) > src\index.js
    echo %GREEN%[OK] Created src\index.js file.%RESET%
)

if not exist src\index.css (
    echo %CYAN%Creating default src\index.css file...%RESET%
    (
        echo @tailwind base;
        echo @tailwind components;
        echo @tailwind utilities;
        echo.
        echo body {
        echo   margin: 0;
        echo   font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
        echo     'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
        echo     sans-serif;
        echo   -webkit-font-smoothing: antialiased;
        echo   -moz-osx-font-smoothing: grayscale;
        echo   background-color: #f3f4f6;
        echo }
        echo.
        echo code {
        echo   font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
        echo     monospace;
        echo }
    ) > src\index.css
    echo %GREEN%[OK] Created src\index.css file.%RESET%
)

:: Create public directory and index.html if they don't exist
if not exist public (
    mkdir public
    echo %GREEN%[OK] Created public directory.%RESET%
    
    echo %CYAN%Creating default public\index.html file...%RESET%
    (
        echo ^<!DOCTYPE html^>
        echo ^<html lang="en"^>
        echo   ^<head^>
        echo     ^<meta charset="utf-8" /^>
        echo     ^<link rel="icon" href="%%PUBLIC_URL%%/favicon.ico" /^>
        echo     ^<meta name="viewport" content="width=device-width, initial-scale=1" /^>
        echo     ^<meta name="theme-color" content="#000000" /^>
        echo     ^<meta name="description" content="GitHub Events Dashboard" /^>
        echo     ^<title^>GitHub Events Dashboard^</title^>
        echo   ^</head^>
        echo   ^<body^>
        echo     ^<noscript^>You need to enable JavaScript to run this app.^</noscript^>
        echo     ^<div id="root"^>^</div^>
        echo   ^</body^>
        echo ^</html^>
    ) > public\index.html
    echo %GREEN%[OK] Created public\index.html file.%RESET%
)

:: Start backend server in a new window with improved error handling
echo %CYAN%Starting backend server...%RESET%
start "GitEvents Backend" cmd /k "color 0A && echo GitEvents Backend Server && echo. && call venv\Scripts\activate.bat && python main.py"
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Failed to start backend server.%RESET%
    echo Attempting to diagnose the issue...
    
    :: Check if main.py exists
    if not exist main.py (
        echo %RED%main.py not found. Project structure may be incorrect.%RESET%
    ) else (
        :: Try to run with more detailed error output
        echo %YELLOW%Running main.py with detailed error output:%RESET%
        call venv\Scripts\activate.bat && python main.py
    )
    
    pause
    exit /b 1
)

:: Wait a moment for the backend to start
echo %CYAN%Waiting for backend to start...%RESET%
timeout /t 5 /nobreak > nul

:: Start frontend server with improved error handling
echo %CYAN%Starting frontend server...%RESET%
start "GitEvents Frontend" cmd /k "color 0B && echo GitEvents Frontend Server && echo. && npm start"
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Failed to start frontend server.%RESET%
    echo Attempting to diagnose the issue...
    
    :: Check if package.json exists
    if not exist package.json (
        echo %RED%package.json not found. Project structure may be incorrect.%RESET%
    ) else (
        :: Try to run with more detailed error output
        echo %YELLOW%Running npm start with detailed error output:%RESET%
        npm start
    )
    
    pause
    exit /b 1
)

echo.
echo %GREEN%[SUCCESS] GitEvents is now running!%RESET%
echo %CYAN%Backend: http://localhost:8001%RESET%
echo %CYAN%Frontend: http://localhost:3000%RESET%
echo.
echo %YELLOW%Press any key to close this window. The servers will continue running.%RESET%
pause > nul
