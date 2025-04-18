@echo off
setlocal enabledelayedexpansion
color 0A

echo +--------------------------------------------------+
echo ^|  GitEvents - Fix React Scripts                    ^|
echo +--------------------------------------------------+
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

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

echo Checking for react-scripts in local dependencies...
call npm list react-scripts >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] react-scripts not found in local dependencies.
    echo Installing react-scripts locally...
    
    call npm install react-scripts --save-dev
    if %ERRORLEVEL% NEQ 0 (
        echo [WARNING] Failed to install react-scripts locally. Trying globally...
        
        call npm install -g react-scripts
        if %ERRORLEVEL% NEQ 0 (
            color 0C
            echo [ERROR] Failed to install react-scripts.
            echo Please try running 'npm install react-scripts' manually.
            pause
            exit /b 1
        ) else (
            color 0A
            echo [OK] react-scripts installed globally.
        )
    ) else (
        color 0A
        echo [OK] react-scripts installed locally.
    )
) else (
    echo [OK] react-scripts is already installed locally.
)

echo.
echo Checking for missing dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    color 0E
    echo [WARNING] Some dependencies could not be installed.
    echo The application may not function correctly.
) else (
    color 0A
    echo [OK] All dependencies are installed.
)

echo.
echo +--------------------------------------------------+
echo ^|  Fix Complete!                                   ^|
echo +--------------------------------------------------+
echo.
echo You can now run InstallAndStart.bat or start.bat to launch the application.
echo.
pause
