@echo off
setlocal enabledelayedexpansion
color 0A

REM Set the working directory to the script's location
cd /d "%~dp0"

REM Windows CMD doesn't support ANSI color codes by default
REM Removing ANSI color codes and using CMD color commands instead

echo ===================================
echo GitEvents - Update, Clean & Refresh
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
color 0A
echo [OK] Git detected.

REM Check if we're in a git repository
if not exist .git (
    color 0C
    echo [ERROR] Not in a Git repository. Please run this script from the GitEvents directory.
    pause
    exit /b 1
)

REM Stop any running GitEvents processes
color 0B
echo Stopping any running GitEvents processes...
taskkill /f /im node.exe /fi "WINDOWTITLE eq GitEvents Frontend*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq GitEvents Backend*" >nul 2>&1
color 0A
echo [OK] Stopped running processes.

REM Backup .env file if it exists
if exist .env (
    color 0B
    echo Backing up .env file...
    copy .env .env.backup >nul
    color 0A
    echo [OK] .env file backed up to .env.backup
)

REM Check for uncommitted changes
color 0B
echo Checking for uncommitted changes...
git diff --quiet --exit-code
if %ERRORLEVEL% NEQ 0 (
    color 0E
    echo [WARNING] You have uncommitted changes in your repository.
    set /p STASH_CHANGES=Would you like to stash these changes? (Y/N): 
    if /i "!STASH_CHANGES!"=="Y" (
        git stash save "Auto-stashed by UpdateAndClean.bat"
        if %ERRORLEVEL% NEQ 0 (
            color 0C
            echo [ERROR] Failed to stash changes.
            set /a ERROR_COUNT+=1
        ) else (
            color 0A
            echo [OK] Changes stashed successfully.
        )
    ) else (
        color 0E
        echo [WARNING] Proceeding with uncommitted changes. This may cause conflicts.
        set /a WARNING_COUNT+=1
    )
)

REM Clean up node_modules and virtual environment
color 0B
echo Cleaning up node_modules and virtual environment...
if exist node_modules (
    color 0B
    echo Removing node_modules...
    rmdir /s /q node_modules
    if exist node_modules (
        color 0E
        echo [WARNING] Could not completely remove node_modules.
        echo Some files may be locked by other processes.
        set /a WARNING_COUNT+=1
    ) else (
        color 0A
        echo [OK] node_modules removed.
    )
)

if exist venv (
    color 0B
    echo Removing virtual environment...
    rmdir /s /q venv
    if exist venv (
        color 0E
        echo [WARNING] Could not completely remove virtual environment.
        echo Some files may be locked by other processes.
        set /a WARNING_COUNT+=1
    ) else (
        color 0A
        echo [OK] Virtual environment removed.
    )
)

REM Reset Git repository to HEAD
color 0B
echo Resetting Git repository to HEAD...
git reset --hard HEAD
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to reset Git repository.
    set /a ERROR_COUNT+=1
) else (
    color 0A
    echo [OK] Git repository reset to HEAD.
)

REM Clean Git repository
color 0B
echo Cleaning Git repository...
git clean -fd
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to clean Git repository.
    set /a ERROR_COUNT+=1
) else (
    color 0A
    echo [OK] Git repository cleaned.
)

REM Pull latest changes
color 0B
echo Pulling latest changes from remote repository...
git pull
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Failed to pull latest changes.
    echo This could be due to network issues or conflicts with the remote repository.
    
    REM Try to diagnose the issue
    color 0B
    echo Attempting to diagnose the issue...
    git remote -v
    echo.
    git status
    
    set /a ERROR_COUNT+=1
) else (
    color 0A
    echo [OK] Latest changes pulled successfully.
)

REM Verify essential files exist after pull
color 0B
echo Verifying essential files...
set MISSING_FILES=0

if not exist main.py (
    color 0C
    echo [ERROR] main.py is missing.
    set /a MISSING_FILES+=1
    set /a ERROR_COUNT+=1
)

if not exist requirements.txt (
    color 0C
    echo [ERROR] requirements.txt is missing.
    set /a MISSING_FILES+=1
    set /a ERROR_COUNT+=1
)

if not exist package.json (
    color 0C
    echo [ERROR] package.json is missing.
    set /a MISSING_FILES+=1
    set /a ERROR_COUNT+=1
)

if %MISSING_FILES% GTR 0 (
    color 0C
    echo [ERROR] Essential files are missing after pull.
    echo Please check your repository and try again.
) else (
    color 0A
    echo [OK] All essential files verified.
)

REM Restore .env file if backup exists
if exist .env.backup (
    color 0B
    echo Restoring .env file from backup...
    copy .env.backup .env >nul
    color 0A
    echo [OK] .env file restored from backup.
)

REM Check if there are any errors
if %ERROR_COUNT% GTR 0 (
    echo.
    color 0C
    echo [CRITICAL] There were %ERROR_COUNT% errors during upgrade.
    echo Please fix these errors before continuing.
    echo.
    pause
    exit /b 1
)

REM Check if there are any warnings
if %WARNING_COUNT% GTR 0 (
    echo.
    color 0E
    echo [WARNING] There were %WARNING_COUNT% warnings during upgrade.
    echo Some operations may not have completed successfully.
    echo.
)

echo.
color 0A
echo ===================================
echo GitEvents Update Complete!
echo ===================================
echo.
echo [SUCCESS] GitEvents has been updated successfully.

REM Ask if user wants to start the deploy script
echo.
choice /C YN /M "Do you want to start the Installation and Startup Script now?"
if %ERRORLEVEL% EQU 1 (
    echo.
    color 0B
    echo Starting installation and startup script...
    call InstallAndStart.bat
) else (
    echo.
    color 0B
    echo To deploy and start the application later, run InstallAndStart.bat
    echo.
    color 0E
    echo Press any key to exit.
    pause > nul
)
