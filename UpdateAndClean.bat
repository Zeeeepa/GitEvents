@echo off
setlocal enabledelayedexpansion
color 0A

REM Set the working directory to the script's location
cd /d "%~dp0"

REM Set color codes for better visibility
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "RESET=[0m"

echo %CYAN%╔══════════════════════════════════════════════════╗%RESET%
echo %CYAN%║  GitEvents - Update, Clean & Refresh             ║%RESET%
echo %CYAN%╚══════════════════════════════════════════════════╝%RESET%
echo.

REM Set error handling
set ERROR_COUNT=0
set WARNING_COUNT=0

REM Check if Git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Git is not installed or not in PATH.%RESET%
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)
echo %GREEN%[OK] Git detected.%RESET%

REM Check if we're in a git repository
if not exist .git (
    echo %RED%[ERROR] Not in a Git repository. Please run this script from the GitEvents directory.%RESET%
    pause
    exit /b 1
)

REM Stop any running GitEvents processes
echo %CYAN%Stopping any running GitEvents processes...%RESET%
taskkill /f /im node.exe /fi "WINDOWTITLE eq GitEvents Frontend*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq GitEvents Backend*" >nul 2>&1
echo %GREEN%[OK] Stopped running processes.%RESET%

REM Backup .env file if it exists
if exist .env (
    echo %CYAN%Backing up .env file...%RESET%
    copy .env .env.backup >nul
    echo %GREEN%[OK] .env file backed up to .env.backup%RESET%
)

REM Check for uncommitted changes
echo %CYAN%Checking for uncommitted changes...%RESET%
git diff --quiet --exit-code
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%[WARNING] You have uncommitted changes in your repository.%RESET%
    set /p STASH_CHANGES=Would you like to stash these changes? (Y/N): 
    if /i "!STASH_CHANGES!"=="Y" (
        git stash save "Auto-stashed by UpdateAndClean.bat"
        if %ERRORLEVEL% NEQ 0 (
            echo %RED%[ERROR] Failed to stash changes.%RESET%
            set /a ERROR_COUNT+=1
        ) else (
            echo %GREEN%[OK] Changes stashed successfully.%RESET%
        )
    ) else (
        echo %YELLOW%[WARNING] Proceeding with uncommitted changes. This may cause conflicts.%RESET%
        set /a WARNING_COUNT+=1
    )
)

REM Clean up node_modules and virtual environment
echo %CYAN%Cleaning up node_modules and virtual environment...%RESET%
if exist node_modules (
    echo %CYAN%Removing node_modules...%RESET%
    rmdir /s /q node_modules
    if exist node_modules (
        echo %YELLOW%[WARNING] Could not completely remove node_modules.%RESET%
        echo Some files may be locked by other processes.
        set /a WARNING_COUNT+=1
    ) else (
        echo %GREEN%[OK] node_modules removed.%RESET%
    )
)

if exist venv (
    echo %CYAN%Removing virtual environment...%RESET%
    rmdir /s /q venv
    if exist venv (
        echo %YELLOW%[WARNING] Could not completely remove virtual environment.%RESET%
        echo Some files may be locked by other processes.
        set /a WARNING_COUNT+=1
    ) else (
        echo %GREEN%[OK] Virtual environment removed.%RESET%
    )
)

REM Reset Git repository to HEAD
echo %CYAN%Resetting Git repository to HEAD...%RESET%
git reset --hard HEAD
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Failed to reset Git repository.%RESET%
    set /a ERROR_COUNT+=1
) else (
    echo %GREEN%[OK] Git repository reset to HEAD.%RESET%
)

REM Clean Git repository
echo %CYAN%Cleaning Git repository...%RESET%
git clean -fd
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Failed to clean Git repository.%RESET%
    set /a ERROR_COUNT+=1
) else (
    echo %GREEN%[OK] Git repository cleaned.%RESET%
)

REM Pull latest changes
echo %CYAN%Pulling latest changes from remote repository...%RESET%
git pull
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Failed to pull latest changes.%RESET%
    echo This could be due to network issues or conflicts with the remote repository.
    
    REM Try to diagnose the issue
    echo %CYAN%Attempting to diagnose the issue...%RESET%
    git remote -v
    echo.
    git status
    
    set /a ERROR_COUNT+=1
) else (
    echo %GREEN%[OK] Latest changes pulled successfully.%RESET%
)

REM Verify essential files exist after pull
echo %CYAN%Verifying essential files...%RESET%
set MISSING_FILES=0

if not exist main.py (
    echo %RED%[ERROR] main.py is missing.%RESET%
    set /a MISSING_FILES+=1
    set /a ERROR_COUNT+=1
)

if not exist requirements.txt (
    echo %RED%[ERROR] requirements.txt is missing.%RESET%
    set /a MISSING_FILES+=1
    set /a ERROR_COUNT+=1
)

if not exist package.json (
    echo %RED%[ERROR] package.json is missing.%RESET%
    set /a MISSING_FILES+=1
    set /a ERROR_COUNT+=1
)

if %MISSING_FILES% GTR 0 (
    echo %RED%[ERROR] Essential files are missing after pull.%RESET%
    echo Please check your repository and try again.
) else (
    echo %GREEN%[OK] All essential files verified.%RESET%
)

REM Restore .env file if backup exists
if exist .env.backup (
    echo %CYAN%Restoring .env file from backup...%RESET%
    copy .env.backup .env >nul
    echo %GREEN%[OK] .env file restored from backup.%RESET%
)

REM Check if there are any errors
if %ERROR_COUNT% GTR 0 (
    echo.
    echo %RED%[CRITICAL] There were %ERROR_COUNT% errors during upgrade.%RESET%
    echo Please fix these errors before continuing.
    echo.
    pause
    exit /b 1
)

REM Check if there are any warnings
if %WARNING_COUNT% GTR 0 (
    echo.
    echo %YELLOW%[WARNING] There were %WARNING_COUNT% warnings during upgrade.%RESET%
    echo Some operations may not have completed successfully.
    echo.
)

echo.
echo %GREEN%╔══════════════════════════════════════════════════╗%RESET%
echo %GREEN%║  GitEvents Update Complete!                      ║%RESET%
echo %GREEN%╚══════════════════════════════════════════════════╝%RESET%
echo.
echo %GREEN%[SUCCESS] GitEvents has been updated successfully.%RESET%

REM Ask if user wants to start the deploy script
echo.
choice /C YN /M "Do you want to start the Installation and Startup Script now?"
if %ERRORLEVEL% EQU 1 (
    echo.
    echo %CYAN%Starting installation and startup script...%RESET%
    call InstallAndStart.bat
) else (
    echo.
    echo %CYAN%To deploy and start the application later, run InstallAndStart.bat%RESET%
    echo.
    echo %YELLOW%Press any key to exit.%RESET%
    pause > nul
)
