@echo off
setlocal enabledelayedexpansion

:: Set color codes for better visibility
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "RESET=[0m"

echo %CYAN%╔════════════════════════════════════════════════════╗%RESET%
echo %CYAN%║  GitEvents - One-Click Deployment and Startup      ║%RESET%
echo %CYAN%╚════════════════════════════════════════════════════╝%RESET%
echo.

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Python is not installed or not in PATH.%RESET%
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Run the Python deployment script
echo %CYAN%Running deployment script...%RESET%
python deploy.py %*

:: If the script exits with an error, pause to show the error message
if %ERRORLEVEL% NEQ 0 (
    echo %RED%Deployment script failed with error code %ERRORLEVEL%%RESET%
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0
