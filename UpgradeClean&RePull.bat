@echo off
setlocal enabledelayedexpansion
color 0A

echo ===================================
echo GitEvents - Upgrade, Clean & Re-Pull
echo ===================================
echo.

REM Set error handling
set ERROR_COUNT=0
set WARNING_COUNT=0

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

REM Stop any running GitEvents processes
echo Stopping any running GitEvents processes...
taskkill /f /im node.exe /fi "WINDOWTITLE eq GitEvents Frontend*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq GitEvents Backend*" >nul 2>&1
echo [OK] Stopped running processes.

REM Backup .env file if it exists
if exist .env (
    echo Backing up .env file...
    copy .env .env.backup >nul
    echo [OK] .env file backed up to .env.backup
)

REM Clean up node_modules and virtual environment
echo Cleaning up node_modules and virtual environment...
if exist node_modules (
    echo Removing node_modules...
    rmdir /s /q node_modules
    if exist node_modules (
        echo [WARNING] Could not completely remove node_modules.
        echo Some files may be locked by other processes.
        set /a WARNING_COUNT+=1
    ) else (
        echo [OK] node_modules removed.
    )
)

if exist venv (
    echo Removing virtual environment...
    rmdir /s /q venv
    if exist venv (
        echo [WARNING] Could not completely remove virtual environment.
        echo Some files may be locked by other processes.
        set /a WARNING_COUNT+=1
    ) else (
        echo [OK] Virtual environment removed.
    )
)

REM Reset Git repository to HEAD
echo Resetting Git repository to HEAD...
git reset --hard HEAD
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to reset Git repository.
    set /a ERROR_COUNT+=1
) else (
    echo [OK] Git repository reset to HEAD.
)

REM Clean Git repository
echo Cleaning Git repository...
git clean -fd
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to clean Git repository.
    set /a ERROR_COUNT+=1
) else (
    echo [OK] Git repository cleaned.
)

REM Pull latest changes
echo Pulling latest changes from remote repository...
git pull
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to pull latest changes.
    echo This could be due to uncommitted changes or network issues.
    set /a ERROR_COUNT+=1
) else (
    echo [OK] Latest changes pulled successfully.
)

REM Verify essential files exist after pull
echo Verifying essential files...
set MISSING_FILES=0

if not exist main.py (
    echo [ERROR] main.py is missing.
    set /a MISSING_FILES+=1
    set /a ERROR_COUNT+=1
)

if not exist requirements.txt (
    echo [ERROR] requirements.txt is missing.
    set /a MISSING_FILES+=1
    set /a ERROR_COUNT+=1
)

if not exist package.json (
    echo [ERROR] package.json is missing.
    set /a MISSING_FILES+=1
    set /a ERROR_COUNT+=1
)

if %MISSING_FILES% GTR 0 (
    color 0C
    echo [ERROR] Essential files are missing after pull.
    echo Please check your repository and try again.
) else (
    echo [OK] All essential files verified.
)

REM Restore .env file if backup exists
if exist .env.backup (
    echo Restoring .env file from backup...
    copy .env.backup .env >nul
    echo [OK] .env file restored from backup.
)

REM Check if there are any errors
if %ERROR_COUNT% GTR 0 (
    color 0C
    echo.
    echo [CRITICAL] There were %ERROR_COUNT% errors during upgrade.
    echo Please fix these errors before continuing.
    echo.
    pause
    exit /b 1
)

REM Check if there are any warnings
if %WARNING_COUNT% GTR 0 (
    color 0E
    echo.
    echo [WARNING] There were %WARNING_COUNT% warnings during upgrade.
    echo Some operations may not have completed successfully.
    echo.
)

color 0A
echo.
echo ===================================
echo GitEvents Upgrade Complete!
echo ===================================
echo.
echo [SUCCESS] GitEvents has been upgraded successfully.
echo To deploy and start the application, run FullDeployLocal^&Start.bat
echo.
echo Press any key to exit.
pause > nul
