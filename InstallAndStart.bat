@echo off
setlocal enabledelayedexpansion
color 0A

REM Set the working directory to the script's location
cd /d "%~dp0"

echo +--------------------------------------------------+
echo ^|  GitEvents - Installation and Startup            ^|
echo +--------------------------------------------------+

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
color 0A
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
color 0A
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
color 0A
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
color 0A
echo [OK] Git detected.

REM Check if we're in a git repository
if not exist .git (
    color 0C
    echo [ERROR] Not in a Git repository. Please run this script from the GitEvents directory.
    pause
    exit /b 1
)

REM Check if .env file exists, if not create with interactive prompts
if not exist .env (
    color 0B
    echo Creating .env file...
    echo # GitEvents Environment Configuration > .env
    
    REM GitHub Configuration
    echo.
    color 0B
    echo ===================================
    echo GitHub Configuration
    echo ===================================
    
    set /p GITHUB_TOKEN=Enter your GitHub API token (or press Enter to use default): 
    if "!GITHUB_TOKEN!"=="" (
        set GITHUB_TOKEN=your_github_token_here
        color 0E
        echo [INFO] Using default GitHub token placeholder. You'll need to update this later.
    ) else (
        color 0A
        echo [OK] GitHub token set.
    )
    echo GITHUB_TOKEN=!GITHUB_TOKEN! >> .env
    
    set /p GITHUB_WEBHOOK_SECRET=Enter your GitHub webhook secret (or press Enter to use default): 
    if "!GITHUB_WEBHOOK_SECRET!"=="" (
        set GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
        color 0E
        echo [INFO] Using default webhook secret placeholder. You'll need to update this later.
    ) else (
        color 0A
        echo [OK] GitHub webhook secret set.
    )
    echo GITHUB_WEBHOOK_SECRET=!GITHUB_WEBHOOK_SECRET! >> .env
    
    REM Database Configuration
    echo.
    color 0B
    echo ===================================
    echo Database Configuration
    echo ===================================
    
    echo Select database type:
    echo 1. SQLite (default, recommended for local development)
    echo 2. MySQL
    set /p DB_TYPE_CHOICE=Enter your choice (1 or 2): 
    
    if "!DB_TYPE_CHOICE!"=="2" (
        echo DB_TYPE=mysql >> .env
        
        set /p DB_HOST=Enter database host (or press Enter for localhost): 
        if "!DB_HOST!"=="" set DB_HOST=localhost
        echo DB_HOST=!DB_HOST! >> .env
        
        set /p DB_PORT=Enter database port (or press Enter for 3306): 
        if "!DB_PORT!"=="" set DB_PORT=3306
        echo DB_PORT=!DB_PORT! >> .env
        
        set /p DB_NAME=Enter database name (or press Enter for github_events): 
        if "!DB_NAME!"=="" set DB_NAME=github_events
        echo DB_NAME=!DB_NAME! >> .env
        
        set /p DB_USER=Enter database username: 
        echo DB_USER=!DB_USER! >> .env
        
        set /p DB_PASSWORD=Enter database password: 
        echo DB_PASSWORD=!DB_PASSWORD! >> .env
        
        color 0A
        echo [OK] MySQL database configuration set.
    ) else (
        set /p GITHUB_EVENTS_DB=Enter SQLite database path (or press Enter for github_events.db): 
        if "!GITHUB_EVENTS_DB!"=="" set GITHUB_EVENTS_DB=github_events.db
        echo GITHUB_EVENTS_DB=!GITHUB_EVENTS_DB! >> .env
        
        color 0A
        echo [OK] SQLite database configuration set.
    )
    
    REM API Configuration
    echo.
    color 0B
    echo ===================================
    echo API Configuration
    echo ===================================
    
    set /p API_PORT=Enter API port (or press Enter for 8001): 
    if "!API_PORT!"=="" set API_PORT=8001
    echo API_PORT=!API_PORT! >> .env
    
    set /p WEBHOOK_PORT=Enter webhook port (or press Enter for 8002): 
    if "!WEBHOOK_PORT!"=="" set WEBHOOK_PORT=8002
    echo WEBHOOK_PORT=!WEBHOOK_PORT! >> .env
    
    REM Frontend Configuration
    echo.
    color 0B
    echo ===================================
    echo Frontend Configuration
    echo ===================================
    
    set /p REACT_APP_API_URL=Enter API URL for frontend (or press Enter for http://localhost:8001/api): 
    if "!REACT_APP_API_URL!"=="" set REACT_APP_API_URL=http://localhost:8001/api
    echo REACT_APP_API_URL=!REACT_APP_API_URL! >> .env
    
    REM Ngrok Configuration
    echo.
    color 0B
    echo ===================================
    echo Ngrok Configuration (Optional)
    echo ===================================
    
    set /p ENABLE_NGROK=Enable Ngrok for webhook tunneling? (true/false, default: false): 
    if "!ENABLE_NGROK!"=="" set ENABLE_NGROK=false
    echo ENABLE_NGROK=!ENABLE_NGROK! >> .env
    
    if "!ENABLE_NGROK!"=="true" (
        set /p NGROK_AUTH_TOKEN=Enter your Ngrok auth token: 
        echo NGROK_AUTH_TOKEN=!NGROK_AUTH_TOKEN! >> .env
    ) else (
        echo NGROK_AUTH_TOKEN=your_ngrok_auth_token_here >> .env
    )
    
    REM Windows-specific Configuration
    echo.
    color 0B
    echo ===================================
    echo Windows Configuration
    echo ===================================
    
    set /p OPEN_BROWSER=Automatically open browser when starting? (true/false, default: true): 
    if "!OPEN_BROWSER!"=="" set OPEN_BROWSER=true
    echo OPEN_BROWSER=!OPEN_BROWSER! >> .env
    
    color 0A
    echo [OK] .env file created successfully.
    echo.
) else (
    color 0E
    echo [INFO] .env file already exists. Checking configuration...
    
    REM Check if essential variables are set in .env
    set MISSING_VARS=0
    
    findstr /C:"GITHUB_TOKEN=your_github_token_here" .env >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        color 0E
        echo [WARNING] GitHub token is not set in .env file.
        set /p UPDATE_TOKEN=Would you like to update it now? (Y/N): 
        if /i "!UPDATE_TOKEN!"=="Y" (
            set /p NEW_TOKEN=Enter your GitHub API token: 
            powershell -Command "(Get-Content .env) -replace 'GITHUB_TOKEN=your_github_token_here', 'GITHUB_TOKEN=!NEW_TOKEN!' | Set-Content .env"
            color 0A
            echo [OK] GitHub token updated.
        ) else (
            set /a WARNING_COUNT+=1
        )
    )
    
    findstr /C:"GITHUB_WEBHOOK_SECRET=your_webhook_secret_here" .env >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        color 0E
        echo [WARNING] GitHub webhook secret is not set in .env file.
        set /p UPDATE_SECRET=Would you like to update it now? (Y/N): 
        if /i "!UPDATE_SECRET!"=="Y" (
            set /p NEW_SECRET=Enter your GitHub webhook secret: 
            powershell -Command "(Get-Content .env) -replace 'GITHUB_WEBHOOK_SECRET=your_webhook_secret_here', 'GITHUB_WEBHOOK_SECRET=!NEW_SECRET!' | Set-Content .env"
            color 0A
            echo [OK] GitHub webhook secret updated.
        ) else (
            set /a WARNING_COUNT+=1
        )
    )
)

REM Create data directory if it doesn't exist
if not exist data (
    mkdir data
    color 0A
    echo [OK] Created data directory.
)

REM Create Python virtual environment
color 0B
echo Creating Python virtual environment...
if exist venv (
    color 0E
    echo [INFO] Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [ERROR] Failed to create virtual environment.
        echo Please check your Python installation.
        set /a ERROR_COUNT+=1
    ) else (
        color 0A
        echo [OK] Virtual environment created.
    )
)

REM Activate virtual environment
color 0B
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to activate virtual environment.
    set /a ERROR_COUNT+=1
) else (
    color 0A
    echo [OK] Virtual environment activated.
)

REM Install Python dependencies
color 0B
echo Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to install Python dependencies.
    echo Please check your requirements.txt file and internet connection.
    set /a ERROR_COUNT+=1
) else (
    color 0A
    echo [OK] Python dependencies installed.
)

REM Create src directory if it doesn't exist
if not exist src (
    mkdir src
    color 0A
    echo [OK] Created src directory.
)

REM Create src/components/dashboard directory if it doesn't exist
if not exist src\components\dashboard (
    mkdir src\components\dashboard
    color 0A
    echo [OK] Created src\components\dashboard directory.
)

REM Create public directory if it doesn't exist
if not exist public (
    mkdir public
    color 0A
    echo [OK] Created public directory.
)

REM Create public/index.html if it doesn't exist
if not exist public\index.html (
    color 0B
    echo Creating public\index.html...
    echo ^<!DOCTYPE html^> > public\index.html
    echo ^<html lang="en"^> >> public\index.html
    echo   ^<head^> >> public\index.html
    echo     ^<meta charset="utf-8" /^> >> public\index.html
    echo     ^<link rel="icon" href="%PUBLIC_URL%/favicon.ico" /^> >> public\index.html
    echo     ^<meta name="viewport" content="width=device-width, initial-scale=1" /^> >> public\index.html
    echo     ^<meta name="theme-color" content="#000000" /^> >> public\index.html
    echo     ^<meta name="description" content="GitHub Events Dashboard" /^> >> public\index.html
    echo     ^<title^>GitHub Events Dashboard^</title^> >> public\index.html
    echo   ^</head^> >> public\index.html
    echo   ^<body^> >> public\index.html
    echo     ^<noscript^>You need to enable JavaScript to run this app.^</noscript^> >> public\index.html
    echo     ^<div id="root"^>^</div^> >> public\index.html
    echo   ^</body^> >> public\index.html
    echo ^</html^> >> public\index.html
    color 0A
    echo [OK] Created public\index.html file.
)

REM Create src/index.js if it doesn't exist
if not exist src\index.js (
    color 0B
    echo Creating src\index.js...
    echo import React from 'react'; > src\index.js
    echo import ReactDOM from 'react-dom/client'; >> src\index.js
    echo import './index.css'; >> src\index.js
    echo import GitHubEventsDashboard from './components/dashboard/GitHubEventsDashboard'; >> src\index.js
    echo. >> src\index.js
    echo const root = ReactDOM.createRoot(document.getElementById('root')); >> src\index.js
    echo root.render( >> src\index.js
    echo   ^<React.StrictMode^> >> src\index.js
    echo     ^<GitHubEventsDashboard /^> >> src\index.js
    echo   ^</React.StrictMode^> >> src\index.js
    echo ); >> src\index.js
    color 0A
    echo [OK] Created src\index.js file.
)

REM Create src/index.css if it doesn't exist
if not exist src\index.css (
    color 0B
    echo Creating src\index.css...
    echo @tailwind base; > src\index.css
    echo @tailwind components; >> src\index.css
    echo @tailwind utilities; >> src\index.css
    echo. >> src\index.css
    echo body { >> src\index.css
    echo   margin: 0; >> src\index.css
    echo   font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', >> src\index.css
    echo     'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', >> src\index.css
    echo     sans-serif; >> src\index.css
    echo   -webkit-font-smoothing: antialiased; >> src\index.css
    echo   -moz-osx-font-smoothing: grayscale; >> src\index.css
    echo   background-color: #f3f4f6; >> src\index.css
    echo } >> src\index.css
    echo. >> src\index.css
    echo code { >> src\index.css
    echo   font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', >> src\index.css
    echo     monospace; >> src\index.css
    echo } >> src\index.css
    color 0A
    echo [OK] Created src\index.css file.
)

REM Copy dashboard components if they exist in the dashboard directory
if exist dashboard\*.jsx (
    color 0B
    echo Copying dashboard components to src\components\dashboard...
    copy dashboard\*.jsx src\components\dashboard\
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [ERROR] Failed to copy dashboard components.
        set /a ERROR_COUNT+=1
    ) else (
        color 0A
        echo [OK] Dashboard components copied.
    )
)

REM Install Node.js dependencies with retry mechanism
color 0B
echo Installing Node.js dependencies...
set RETRY_COUNT=0
:RETRY_NPM
call npm install
if %ERRORLEVEL% NEQ 0 (
    set /a RETRY_COUNT+=1
    if %RETRY_COUNT% LSS 3 (
        color 0E
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
    color 0A
    echo [OK] Node.js dependencies installed successfully.
)

REM Fix npm vulnerabilities
color 0B
echo Fixing npm vulnerabilities...
call npm audit fix --force
if %ERRORLEVEL% NEQ 0 (
    color 0E
    echo [WARNING] Could not fix all npm vulnerabilities.
    echo The application may have security issues.
    set /a WARNING_COUNT+=1
) else (
    color 0A
    echo [OK] npm vulnerabilities fixed.
)

REM Initialize database
color 0B
echo Initializing database...
python -c "from db.db_manager import DatabaseManager; db = DatabaseManager(); db.initialize_database()"
if %ERRORLEVEL% NEQ 0 (
    color 0E
    echo [WARNING] Database initialization may have issues.
    set /a WARNING_COUNT+=1
) else (
    color 0A
    echo [OK] Database initialized.
)

REM Check if there are any errors
if %ERROR_COUNT% GTR 0 (
    echo.
    color 0C
    echo [CRITICAL] There were %ERROR_COUNT% errors during deployment.
    echo Please fix these errors before continuing.
    echo.
    pause
    exit /b 1
)

REM Check if there are any warnings
if %WARNING_COUNT% GTR 0 (
    echo.
    color 0E
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
color 0B
echo Starting backend server...
start "GitEvents Backend" cmd /k "cd /d "%~dp0" && color 0A && echo GitEvents Backend Server && echo. && call venv\Scripts\activate.bat && python main.py"

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to start backend server.
    pause
    exit /b 1
)

REM Wait a moment for the backend to start
color 0B
echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

REM Start frontend server
color 0B
echo Starting frontend server...
start "GitEvents Frontend" cmd /k "cd /d "%~dp0" && color 0B && echo GitEvents Frontend Server && echo. && npm start"

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to start frontend server.
    pause
    exit /b 1
)

REM Check if browser should be opened automatically
findstr /C:"OPEN_BROWSER=true" .env >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    color 0B
    echo Opening browser...
    timeout /t 3 /nobreak > nul
    start http://localhost:3000
)

echo.
color 0A
echo +--------------------------------------------------+
echo ^|  GitEvents Deployment Complete!                  ^|
echo +--------------------------------------------------+

echo.
color 0A
echo [SUCCESS] GitEvents is now running!
color 0B
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo.
color 0E
echo Press any key to close this window. The servers will continue running.
pause > nul
