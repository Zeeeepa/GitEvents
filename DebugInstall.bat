@echo off
setlocal enabledelayedexpansion
color 0A

REM Set the working directory to the script's location
cd /d "%~dp0"

echo +--------------------------------------------------+
echo ^|  GitEvents - Debug Installation                  ^|
echo +--------------------------------------------------+

echo.
echo This script will help diagnose installation issues.
echo.

REM Check environment
echo Checking environment...
echo.

echo System Information:
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"
echo.

echo Path Environment Variable:
echo %PATH%
echo.

REM Check required tools
echo Checking required tools...
echo.

echo Python:
where python 2>nul && (
    python --version
    echo Python path: 
    where python
) || (
    echo Python not found in PATH
)
echo.

echo Node.js:
where node 2>nul && (
    node --version
    echo Node.js path:
    where node
) || (
    echo Node.js not found in PATH
)
echo.

echo npm:
where npm 2>nul && (
    npm --version
    echo npm path:
    where npm
) || (
    echo npm not found in PATH
)
echo.

echo Git:
where git 2>nul && (
    git --version
    echo Git path:
    where git
) || (
    echo Git not found in PATH
)
echo.

REM Check repository status
echo Checking repository status...
echo.

if exist .git (
    echo Git repository found
    git status
    echo.
    echo Remote repositories:
    git remote -v
) else (
    echo Not a Git repository
)
echo.

REM Check file structure
echo Checking file structure...
echo.

echo Required files:
if exist main.py (
    echo [OK] main.py exists
) else (
    echo [MISSING] main.py
)

if exist requirements.txt (
    echo [OK] requirements.txt exists
) else (
    echo [MISSING] requirements.txt
)

if exist package.json (
    echo [OK] package.json exists
) else (
    echo [MISSING] package.json
)

if exist .env (
    echo [OK] .env exists
) else (
    echo [MISSING] .env
)
echo.

echo Directory structure:
dir /B /AD
echo.

REM Check Python environment
echo Checking Python environment...
echo.

if exist venv (
    echo Virtual environment exists
    if exist venv\Scripts\activate.bat (
        echo [OK] Activation script exists
        
        echo Attempting to activate virtual environment...
        call venv\Scripts\activate.bat 2>nul
        
        if defined VIRTUAL_ENV (
            echo [OK] Virtual environment activated
            echo Installed packages:
            pip list
        ) else (
            echo [ERROR] Failed to activate virtual environment
        )
    ) else (
        echo [ERROR] Activation script missing
    )
) else (
    echo Virtual environment does not exist
)
echo.

REM Check Node.js environment
echo Checking Node.js environment...
echo.

if exist node_modules (
    echo node_modules directory exists
    echo Installed packages:
    npm list --depth=0
) else (
    echo node_modules directory does not exist
)
echo.

REM Check database
echo Checking database...
echo.

if exist .env (
    echo Database configuration:
    findstr /C:"DB_TYPE" /C:"GITHUB_EVENTS_DB" /C:"DB_HOST" /C:"DB_PORT" /C:"DB_NAME" .env
    
    for /f "tokens=2 delims==" %%a in ('findstr /C:"GITHUB_EVENTS_DB=" .env') do (
        set DB_PATH=%%a
        if exist "!DB_PATH!" (
            echo [OK] SQLite database exists at !DB_PATH!
        ) else (
            echo [MISSING] SQLite database at !DB_PATH!
        )
    )
) else (
    echo Cannot check database configuration (.env file missing)
)
echo.

echo +--------------------------------------------------+
echo ^|  Debug Information Complete                      ^|
echo +--------------------------------------------------+
echo.
echo Please review the information above to diagnose installation issues.
echo.
echo If you need to reinstall, try running:
echo 1. UpdateAndClean.bat (to clean the environment)
echo 2. InstallAndStart.bat (to reinstall and start the application)
echo.
echo Press any key to exit...
pause > nul
