@echo off
setlocal enabledelayedexpansion
color 0E

echo ===================================
echo GitEvents - Upgrade, Clean ^& Re-Pull
echo ===================================
echo.

REM Check if Git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git is not installed or not in PATH.
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)
echo [OK] Git detected.

REM Check if we're in a git repository
if not exist .git (
    echo [ERROR] Not in a Git repository. Please run this script from the GitEvents directory.
    pause
    exit /b 1
)

REM Stop any running processes
echo Stopping any running GitEvents processes...
taskkill /f /fi "WINDOWTITLE eq GitEvents Backend" >nul 2>nul
taskkill /f /fi "WINDOWTITLE eq GitEvents Frontend" >nul 2>nul
echo [OK] Processes stopped.

REM Clean up node_modules and temporary files
echo Cleaning up node_modules and temporary files...
if exist node_modules (
    rmdir /s /q node_modules
    if %ERRORLEVEL% NEQ 0 (
        echo [WARNING] Could not remove node_modules completely.
        echo Some files might be locked by other processes.
    ) else (
        echo [OK] node_modules removed.
    )
)

REM Clean up Python virtual environment
echo Cleaning up Python virtual environment...
if exist venv (
    rmdir /s /q venv
    if %ERRORLEVEL% NEQ 0 (
        echo [WARNING] Could not remove venv completely.
        echo Some files might be locked by other processes.
    ) else (
        echo [OK] venv removed.
    )
)

REM Clean npm cache
echo Cleaning npm cache...
call npm cache clean --force
echo [OK] npm cache cleaned.

REM Reset Git repository to HEAD
echo Resetting Git repository...
git reset --hard HEAD
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to reset Git repository.
    pause
    exit /b 1
)
echo [OK] Git repository reset.

REM Pull latest changes
echo Pulling latest changes from remote repository...
git pull
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to pull latest changes.
    echo This could be due to local changes or network issues.
    pause
    exit /b 1
)
echo [OK] Latest changes pulled successfully.

REM Check for package.json updates
echo Checking for package.json updates...
if exist package.json (
    echo [OK] package.json exists.
) else (
    echo [ERROR] package.json not found after pull.
    pause
    exit /b 1
)

REM Check for requirements.txt updates
echo Checking for requirements.txt updates...
if exist requirements.txt (
    echo [OK] requirements.txt exists.
) else (
    echo [ERROR] requirements.txt not found after pull.
    pause
    exit /b 1
)

echo.
echo ===================================
echo Upgrade, Clean ^& Re-Pull Complete!
echo ===================================
echo.
echo The repository has been cleaned and updated to the latest version.
echo To deploy and start the application, run FullDeployLocal^&Start.bat
echo.
pause
