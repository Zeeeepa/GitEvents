@echo off
setlocal enabledelayedexpansion
color 0A

cd /d "%~dp0"

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "RESET=[0m"

echo %CYAN%╔════════════════════════════════════════════════╗%RESET%
echo %CYAN%║  GitEvents - Installation and Startup            ║%RESET%
echo %CYAN%╚════════════════════════════════════════════════╝%RESET%
echo.

set ERROR_COUNT=0
set WARNING_COUNT=0

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Python is not installed or not in PATH.%RESET%
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

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

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Node.js is not installed or not in PATH.%RESET%
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

node -v > temp_version.txt
set /p NODE_VERSION=<temp_version.txt
del temp_version.txt
echo %GREEN%[OK] Node.js %NODE_VERSION% detected.%RESET%

where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] npm is not installed or not in PATH.%RESET%
    echo Please reinstall Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo %GREEN%[OK] npm detected.%RESET%

where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Git is not installed or not in PATH.%RESET%
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)
echo %GREEN%[OK] Git detected.%RESET%

if not exist .git (
    echo %RED%[ERROR] Not in a Git repository. Please run this script from the GitEvents directory.%RESET%
    pause
    exit /b 1
)

if not exist .env (
    echo %CYAN%Creating .env file...%RESET%
    echo # GitEvents Environment Configuration > .env
    
    echo.
    echo %CYAN%===================================
    echo GitHub Configuration
    echo ===================================%RESET%
    
    set /p GITHUB_TOKEN=Enter your GitHub API token (or press Enter to use default): 
    if "!GITHUB_TOKEN!"=="" (
        set GITHUB_TOKEN=your_github_token_here
        echo %YELLOW%[INFO] Using default GitHub token placeholder. You'll need to update this later.%RESET%
    ) else (
        echo %GREEN%[OK] GitHub token set.%RESET%
    )
    echo GITHUB_TOKEN=!GITHUB_TOKEN! >> .env
    
    set /p GITHUB_WEBHOOK_SECRET=Enter your GitHub webhook secret (or press Enter to use default): 
    if "!GITHUB_WEBHOOK_SECRET!"=="" (
        set GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
        echo %YELLOW%[INFO] Using default webhook secret placeholder. You'll need to update this later.%RESET%
    ) else (
        echo %GREEN%[OK] GitHub webhook secret set.%RESET%
    )
    echo GITHUB_WEBHOOK_SECRET=!GITHUB_WEBHOOK_SECRET! >> .env
    
    echo.
    echo %CYAN%===================================
    echo Database Configuration
    echo ===================================%RESET%
    
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
        
        echo %GREEN%[OK] MySQL database configuration set.%RESET%
    ) else (
        set /p GITHUB_EVENTS_DB=Enter SQLite database path (or press Enter for github_events.db): 
        if "!GITHUB_EVENTS_DB!"=="" set GITHUB_EVENTS_DB=github_events.db
        echo GITHUB_EVENTS_DB=!GITHUB_EVENTS_DB! >> .env
        
        echo %GREEN%[OK] SQLite database configuration set.%RESET%
    )
    
    echo.
    echo %CYAN%===================================
    echo API Configuration
    echo ===================================%RESET%
    
    set /p API_PORT=Enter API port (or press Enter for 8001): 
    if "!API_PORT!"=="" set API_PORT=8001
    echo API_PORT=!API_PORT! >> .env
    
    set /p WEBHOOK_PORT=Enter webhook port (or press Enter for 8002): 
    if "!WEBHOOK_PORT!"=="" set WEBHOOK_PORT=8002
    echo WEBHOOK_PORT=!WEBHOOK_PORT! >> .env
    
    echo.
    echo %CYAN%===================================
    echo Frontend Configuration
    echo ===================================%RESET%
    
    set /p REACT_APP_API_URL=Enter API URL for frontend (or press Enter for http://localhost:8001/api): 
    if "!REACT_APP_API_URL!"=="" set REACT_APP_API_URL=http://localhost:8001/api
    echo REACT_APP_API_URL=!REACT_APP_API_URL! >> .env
    
    echo.
    echo %CYAN%===================================
    echo Ngrok Configuration (Optional)
    echo ===================================%RESET%
    
    set /p ENABLE_NGROK=Enable Ngrok for webhook tunneling? (true/false, default: false): 
    if "!ENABLE_NGROK!"=="" set ENABLE_NGROK=false
    echo ENABLE_NGROK=!ENABLE_NGROK! >> .env
    
    if "!ENABLE_NGROK!"=="true" (
        set /p NGROK_AUTH_TOKEN=Enter your Ngrok auth token: 
        echo NGROK_AUTH_TOKEN=!NGROK_AUTH_TOKEN! >> .env
    ) else (
        echo NGROK_AUTH_TOKEN=your_ngrok_auth_token_here >> .env
    )
    
    echo.
    echo %CYAN%===================================
    echo Windows Configuration
    echo ===================================%RESET%
    
    set /p OPEN_BROWSER=Automatically open browser when starting? (true/false, default: true): 
    if "!OPEN_BROWSER!"=="" set OPEN_BROWSER=true
    echo OPEN_BROWSER=!OPEN_BROWSER! >> .env
    
    echo %GREEN%[OK] .env file created successfully.%RESET%
    echo.
) else (
    echo %YELLOW%[INFO] .env file already exists. Checking configuration...%RESET%
    
    set MISSING_VARS=0
    
    findstr /C:"GITHUB_TOKEN=your_github_token_here" .env >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo %YELLOW%[WARNING] GitHub token is not set in .env file.%RESET%
        set /p UPDATE_TOKEN=Would you like to update it now? (Y/N): 
        if /i "!UPDATE_TOKEN!"=="Y" (
            set /p NEW_TOKEN=Enter your GitHub API token: 
            powershell -Command "(Get-Content .env) -replace 'GITHUB_TOKEN=your_github_token_here', 'GITHUB_TOKEN=!NEW_TOKEN!' | Set-Content .env"
            echo %GREEN%[OK] GitHub token updated.%RESET%
        ) else (
            set /a WARNING_COUNT+=1
        )
    )
    
    findstr /C:"GITHUB_WEBHOOK_SECRET=your_webhook_secret_here" .env >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo %YELLOW%[WARNING] GitHub webhook secret is not set in .env file.%RESET%
        set /p UPDATE_SECRET=Would you like to update it now? (Y/N): 
        if /i "!UPDATE_SECRET!"=="Y" (
            set /p NEW_SECRET=Enter your GitHub webhook secret: 
            powershell -Command "(Get-Content .env) -replace 'GITHUB_WEBHOOK_SECRET=your_webhook_secret_here', 'GITHUB_WEBHOOK_SECRET=!NEW_SECRET!' | Set-Content .env"
            echo %GREEN%[OK] GitHub webhook secret updated.%RESET%
        ) else (
            set /a WARNING_COUNT+=1
        )
    )
)

if not exist data (
    mkdir data
    echo %GREEN%[OK] Created data directory.%RESET%
)

echo %CYAN%Creating Python virtual environment...%RESET%
if exist venv (
    echo %YELLOW%[INFO] Virtual environment already exists. Skipping creation.%RESET%
) else (
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo %RED%[ERROR] Failed to create virtual environment.%RESET%
        echo Please check your Python installation.
        set /a ERROR_COUNT+=1
    ) else (
        echo %GREEN%[OK] Virtual environment created.%RESET%
    )
)

echo %CYAN%Activating virtual environment...%RESET%
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Failed to activate virtual environment.%RESET%
    set /a ERROR_COUNT+=1
) else (
    echo %GREEN%[OK] Virtual environment activated.%RESET%
)

echo %CYAN%Installing Python dependencies...%RESET%
set RETRY_COUNT=0
:RETRY_PIP
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    set /a RETRY_COUNT+=1
    if %RETRY_COUNT% LSS 3 (
        echo %YELLOW%[WARNING] Failed to install some Python dependencies. Retrying... (Attempt %RETRY_COUNT% of 3)%RESET%
        timeout /t 3 /nobreak > nul
        goto RETRY_PIP
    ) else (
        echo %YELLOW%[WARNING] Some Python dependencies failed to install after 3 attempts.%RESET%
        echo The application may not function correctly.
        set /a WARNING_COUNT+=1
    )
) else (
    echo %GREEN%[OK] Python dependencies installed successfully.%RESET%
)

echo %CYAN%Ensuring React app directories exist...%RESET%
if not exist src (
    mkdir src
    echo %GREEN%[OK] Created src directory.%RESET%
)

if not exist src\components (
    mkdir src\components
    echo %GREEN%[OK] Created src\components directory.%RESET%
)

if not exist src\components\dashboard (
    mkdir src\components\dashboard
    echo %GREEN%[OK] Created src\components\dashboard directory.%RESET%
)

if not exist public (
    mkdir public
    echo %GREEN%[OK] Created public directory.%RESET%
)

if not exist public\index.html (
    echo %CYAN%Creating public\index.html...%RESET%
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
    echo %GREEN%[OK] Created public\index.html file.%RESET%
)

if not exist src\index.js (
    echo %CYAN%Creating src\index.js...%RESET%
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
    echo %GREEN%[OK] Created src\index.js file.%RESET%
)

if not exist src\index.css (
    echo %CYAN%Creating src\index.css...%RESET%
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
    echo %GREEN%[OK] Created src\index.css file.%RESET%
)

if exist dashboard\*.jsx (
    echo %CYAN%Copying dashboard components to src\components\dashboard...%RESET%
    copy dashboard\*.jsx src\components\dashboard\
    if %ERRORLEVEL% NEQ 0 (
        echo %RED%[ERROR] Failed to copy dashboard components.%RESET%
        set /a ERROR_COUNT+=1
    ) else (
        echo %GREEN%[OK] Dashboard components copied.%RESET%
    )
)

echo %CYAN%Installing Node.js dependencies...%RESET%
set RETRY_COUNT=0
:RETRY_NPM
call npm install
if %ERRORLEVEL% NEQ 0 (
    set /a RETRY_COUNT+=1
    if %RETRY_COUNT% LSS 3 (
        echo %YELLOW%[WARNING] Failed to install some Node.js dependencies. Retrying... (Attempt %RETRY_COUNT% of 3)%RESET%
        timeout /t 3 /nobreak > nul
        goto RETRY_NPM
    ) else (
        echo %YELLOW%[WARNING] Some Node.js dependencies failed to install after 3 attempts.%RESET%
        echo The frontend may not function correctly.
        set /a WARNING_COUNT+=1
    )
) else (
    echo %GREEN%[OK] Node.js dependencies installed successfully.%RESET%
)

echo %CYAN%Fixing npm vulnerabilities...%RESET%
call npm audit fix --force
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%[WARNING] Could not fix all npm vulnerabilities.%RESET%
    echo The application may have security issues.
    set /a WARNING_COUNT+=1
) else (
    echo %GREEN%[OK] npm vulnerabilities fixed.%RESET%
)

echo %CYAN%Checking and fixing React component imports...%RESET%
if exist scripts\postinstall.js (
    powershell -Command "(Get-Content scripts\postinstall.js) -replace 'import GitHubEventsDashboard from ''\.\.\/dashboard\/GitHubEventsDashboard'';', 'import GitHubEventsDashboard from ''\.\/components\/dashboard\/GitHubEventsDashboard'';' | Set-Content scripts\postinstall.js"
    echo %GREEN%[OK] Fixed component import paths.%RESET%
)

set DB_TYPE=sqlite
findstr /C:"DB_TYPE=mysql" .env >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set DB_TYPE=mysql
)

if "%DB_TYPE%"=="sqlite" (
    set DB_PATH=github_events.db
    for /f "tokens=2 delims==" %%a in ('findstr /C:"GITHUB_EVENTS_DB=" .env') do (
        set DB_PATH=%%a
    )
    
    if not exist "!DB_PATH!" (
        echo %CYAN%Initializing SQLite database...%RESET%
        python -c "from db.db_manager import DatabaseManager; db = DatabaseManager('!DB_PATH!'); db.initialize_database()"
        if %ERRORLEVEL% NEQ 0 (
            echo %RED%[ERROR] Failed to initialize database.%RESET%
            echo This could be due to missing Python modules or incorrect database configuration.
            echo Please check your Python installation and requirements.txt file.
            set /a ERROR_COUNT+=1
        ) else (
            echo %GREEN%[OK] Database initialized.%RESET%
        )
    ) else (
        echo %YELLOW%[INFO] SQLite database already exists at !DB_PATH!%RESET%
        set /p REINIT_DB=Would you like to reinitialize the database? (Y/N): 
        if /i "!REINIT_DB!"=="Y" (
            echo %CYAN%Reinitializing SQLite database...%RESET%
            python -c "from db.db_manager import DatabaseManager; db = DatabaseManager('!DB_PATH!'); db.initialize_database()"
            if %ERRORLEVEL% NEQ 0 (
                echo %RED%[ERROR] Failed to reinitialize database.%RESET%
                set /a ERROR_COUNT+=1
            ) else (
                echo %GREEN%[OK] Database reinitialized.%RESET%
            )
        )
    )
) else (
    echo %CYAN%Checking MySQL database connection...%RESET%
    for /f "tokens=2 delims==" %%a in ('findstr /C:"DB_HOST=" .env') do set DB_HOST=%%a
    for /f "tokens=2 delims==" %%a in ('findstr /C:"DB_PORT=" .env') do set DB_PORT=%%a
    for /f "tokens=2 delims==" %%a in ('findstr /C:"DB_NAME=" .env') do set DB_NAME=%%a
    for /f "tokens=2 delims==" %%a in ('findstr /C:"DB_USER=" .env') do set DB_USER=%%a
    for /f "tokens=2 delims==" %%a in ('findstr /C:"DB_PASSWORD=" .env') do set DB_PASSWORD=%%a
    
    echo %CYAN%Testing connection to MySQL database at !DB_HOST!:!DB_PORT!/!DB_NAME!...%RESET%
    python -c "from db.db_manager import DatabaseManager; db_config = {'type': 'mysql', 'host': '!DB_HOST!', 'port': '!DB_PORT!', 'name': '!DB_NAME!', 'user': '!DB_USER!', 'password': '!DB_PASSWORD!'}; db = DatabaseManager(); result = db.test_connection(db_config); print(result['message']); exit(0 if result['success'] else 1)"
    if %ERRORLEVEL% NEQ 0 (
        echo %RED%[ERROR] Failed to connect to MySQL database.%RESET%
        set /a ERROR_COUNT+=1
    ) else (
        echo %CYAN%Initializing MySQL database...%RESET%
        python -c "from db.db_manager import DatabaseManager; db = DatabaseManager(); db.initialize_database()"
        if %ERRORLEVEL% NEQ 0 (
            echo %RED%[ERROR] Failed to initialize MySQL database.%RESET%
            set /a ERROR_COUNT+=1
        ) else (
            echo %GREEN%[OK] MySQL database initialized.%RESET%
        )
    )
)

if %ERROR_COUNT% GTR 0 (
    echo.
    echo %RED%[CRITICAL] There were %ERROR_COUNT% errors during deployment.%RESET%
    echo Please fix these errors before continuing.
    echo.
    pause
    exit /b 1
)

if %WARNING_COUNT% GTR 0 (
    echo.
    echo %YELLOW%[WARNING] There were %WARNING_COUNT% warnings during deployment.%RESET%
    echo The application may not function correctly.
    echo.
    choice /C YN /M "Do you want to continue anyway?"
    if !ERRORLEVEL! EQU 2 (
        echo Deployment aborted by user.
        pause
        exit /b 1
    )
)

echo %CYAN%Starting backend server...%RESET%
start "GitEvents Backend" cmd /c "cd /d "%~dp0" && color 0A && echo GitEvents Backend Server && echo. && call venv\Scripts\activate.bat && python main.py"
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Failed to start backend server.%RESET%
    pause
    exit /b 1
)

echo %CYAN%Waiting for backend to start...%RESET%
timeout /t 5 /nobreak > nul

echo %CYAN%Starting frontend server...%RESET%
start "GitEvents Frontend" cmd /c "cd /d "%~dp0" && color 0B && echo GitEvents Frontend Server && echo. && npm start"
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Failed to start frontend server.%RESET%
    pause
    exit /b 1
)

findstr /C:"OPEN_BROWSER=true" .env >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo %CYAN%Opening browser...%RESET%
    timeout /t 3 /nobreak > nul
    start http://localhost:3000
)

echo.
echo %GREEN%╔════════════════════════════════════════════════╗%RESET%
echo %GREEN%║  GitEvents Deployment Complete!                  ║%RESET%
echo %GREEN%╚════════════════════════════════════════════════╝%RESET%
echo.
echo %GREEN%[SUCCESS] GitEvents is now running!%RESET%
echo %CYAN%Backend: http://localhost:8001%RESET%
echo %CYAN%Frontend: http://localhost:3000%RESET%
echo.
echo %YELLOW%Press any key to close this window. The servers will continue running.%RESET%
pause > nul
