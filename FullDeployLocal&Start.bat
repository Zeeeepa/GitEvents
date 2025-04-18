@echo off
setlocal enabledelayedexpansion
color 0A

REM Set the working directory to the script's location
cd /d "%~dp0"

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

REM Check if .env file exists, if not create with interactive prompts
if not exist .env (
    echo Creating .env file...
    echo # GitEvents Environment Configuration > .env
    
    REM GitHub Configuration
    echo.
    echo ===================================
    echo GitHub Configuration
    echo ===================================
    
    set /p GITHUB_TOKEN=Enter your GitHub API token (or press Enter to use default): 
    if "!GITHUB_TOKEN!"=="" (
        set GITHUB_TOKEN=your_github_token_here
        echo [INFO] Using default GitHub token placeholder. You'll need to update this later.
    ) else (
        echo [OK] GitHub token set.
    )
    echo GITHUB_TOKEN=!GITHUB_TOKEN! >> .env
    
    set /p GITHUB_WEBHOOK_SECRET=Enter your GitHub webhook secret (or press Enter to use default): 
    if "!GITHUB_WEBHOOK_SECRET!"=="" (
        set GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
        echo [INFO] Using default webhook secret placeholder. You'll need to update this later.
    ) else (
        echo [OK] GitHub webhook secret set.
    )
    echo GITHUB_WEBHOOK_SECRET=!GITHUB_WEBHOOK_SECRET! >> .env
    
    REM Database Configuration
    echo.
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
        
        echo [OK] MySQL database configuration set.
    ) else (
        set /p GITHUB_EVENTS_DB=Enter SQLite database path (or press Enter for github_events.db): 
        if "!GITHUB_EVENTS_DB!"=="" set GITHUB_EVENTS_DB=github_events.db
        echo GITHUB_EVENTS_DB=!GITHUB_EVENTS_DB! >> .env
        
        echo [OK] SQLite database configuration set.
    )
    
    REM API Configuration
    echo.
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
    echo ===================================
    echo Frontend Configuration
    echo ===================================
    
    set /p REACT_APP_API_URL=Enter API URL for frontend (or press Enter for http://localhost:8001/api): 
    if "!REACT_APP_API_URL!"=="" set REACT_APP_API_URL=http://localhost:8001/api
    echo REACT_APP_API_URL=!REACT_APP_API_URL! >> .env
    
    REM Ngrok Configuration
    echo.
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
    echo ===================================
    echo Windows Configuration
    echo ===================================
    
    set /p OPEN_BROWSER=Automatically open browser when starting? (true/false, default: true): 
    if "!OPEN_BROWSER!"=="" set OPEN_BROWSER=true
    echo OPEN_BROWSER=!OPEN_BROWSER! >> .env
    
    echo [OK] .env file created successfully.
    echo.
) else (
    echo [INFO] .env file already exists. Skipping configuration.
    
    REM Check if essential variables are set in .env
    set MISSING_VARS=0
    
    findstr /C:"GITHUB_TOKEN=your_github_token_here" .env >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [WARNING] GitHub token is not set in .env file.
        set /p UPDATE_TOKEN=Would you like to update it now? (Y/N): 
        if /i "!UPDATE_TOKEN!"=="Y" (
            set /p NEW_TOKEN=Enter your GitHub API token: 
            powershell -Command "(Get-Content .env) -replace 'GITHUB_TOKEN=your_github_token_here', 'GITHUB_TOKEN=!NEW_TOKEN!' | Set-Content .env"
            echo [OK] GitHub token updated.
        ) else (
            set /a WARNING_COUNT+=1
        )
    )
    
    findstr /C:"GITHUB_WEBHOOK_SECRET=your_webhook_secret_here" .env >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [WARNING] GitHub webhook secret is not set in .env file.
        set /p UPDATE_SECRET=Would you like to update it now? (Y/N): 
        if /i "!UPDATE_SECRET!"=="Y" (
            set /p NEW_SECRET=Enter your GitHub webhook secret: 
            powershell -Command "(Get-Content .env) -replace 'GITHUB_WEBHOOK_SECRET=your_webhook_secret_here', 'GITHUB_WEBHOOK_SECRET=!NEW_SECRET!' | Set-Content .env"
            echo [OK] GitHub webhook secret updated.
        ) else (
            set /a WARNING_COUNT+=1
        )
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

REM Fix the postinstall.js script to use the correct import path
echo Checking and fixing React component imports...
if exist scripts\postinstall.js (
    powershell -Command "(Get-Content scripts\postinstall.js) -replace 'import GitHubEventsDashboard from ''\.\.\/dashboard\/GitHubEventsDashboard'';', 'import GitHubEventsDashboard from ''\.\/components\/dashboard\/GitHubEventsDashboard'';' | Set-Content scripts\postinstall.js"
    echo [OK] Fixed component import paths.
)

REM Ensure src/components/dashboard directory exists
if not exist src\components\dashboard (
    mkdir src\components\dashboard
    echo [OK] Created src\components\dashboard directory.
)

REM Copy dashboard components if they exist in the dashboard directory
if exist dashboard\*.jsx (
    echo Copying dashboard components to src\components\dashboard...
    copy dashboard\*.jsx src\components\dashboard\
    echo [OK] Dashboard components copied.
)

REM Check if database exists, if not create it
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
        echo Initializing SQLite database...
        python -c "from db.db_manager import DatabaseManager; db = DatabaseManager('!DB_PATH!'); db.initialize_database()"
        if %ERRORLEVEL% NEQ 0 (
            color 0C
            echo [ERROR] Failed to initialize database.
            set /a ERROR_COUNT+=1
        ) else (
            echo [OK] Database initialized.
        )
    ) else (
        echo [INFO] SQLite database already exists at !DB_PATH!
        set /p REINIT_DB=Would you like to reinitialize the database? (Y/N): 
        if /i "!REINIT_DB!"=="Y" (
            echo Reinitializing SQLite database...
            python -c "from db.db_manager import DatabaseManager; db = DatabaseManager('!DB_PATH!'); db.initialize_database()"
            if %ERRORLEVEL% NEQ 0 (
                color 0C
                echo [ERROR] Failed to reinitialize database.
                set /a ERROR_COUNT+=1
            ) else (
                echo [OK] Database reinitialized.
            )
        )
    )
) else (
    echo Checking MySQL database connection...
    for /f "tokens=2 delims==" %%a in ('findstr /C:"DB_HOST=" .env') do set DB_HOST=%%a
    for /f "tokens=2 delims==" %%a in ('findstr /C:"DB_PORT=" .env') do set DB_PORT=%%a
    for /f "tokens=2 delims==" %%a in ('findstr /C:"DB_NAME=" .env') do set DB_NAME=%%a
    for /f "tokens=2 delims==" %%a in ('findstr /C:"DB_USER=" .env') do set DB_USER=%%a
    for /f "tokens=2 delims==" %%a in ('findstr /C:"DB_PASSWORD=" .env') do set DB_PASSWORD=%%a
    
    echo Testing connection to MySQL database at !DB_HOST!:!DB_PORT!/!DB_NAME!...
    python -c "from db.db_manager import DatabaseManager; db_config = {'type': 'mysql', 'host': '!DB_HOST!', 'port': '!DB_PORT!', 'name': '!DB_NAME!', 'user': '!DB_USER!', 'password': '!DB_PASSWORD!'}; db = DatabaseManager(); result = db.test_connection(db_config); print(result['message']); exit(0 if result['success'] else 1)"
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [ERROR] Failed to connect to MySQL database.
        set /a ERROR_COUNT+=1
    ) else (
        echo Initializing MySQL database...
        python -c "from db.db_manager import DatabaseManager; db = DatabaseManager(); db.initialize_database()"
        if %ERRORLEVEL% NEQ 0 (
            color 0C
            echo [ERROR] Failed to initialize MySQL database.
            set /a ERROR_COUNT+=1
        ) else (
            echo [OK] MySQL database initialized.
        )
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
start "GitEvents Backend" cmd /c "cd /d "%~dp0" && color 0A && echo GitEvents Backend Server && echo. && call venv\Scripts\activate.bat && python main.py"
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
start "GitEvents Frontend" cmd /c "cd /d "%~dp0" && color 0B && echo GitEvents Frontend Server && echo. && npm start"
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to start frontend server.
    pause
    exit /b 1
)

REM Check if browser should be opened automatically
findstr /C:"OPEN_BROWSER=true" .env >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Opening browser...
    timeout /t 3 /nobreak > nul
    start http://localhost:3000
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
