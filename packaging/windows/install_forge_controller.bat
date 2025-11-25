@echo off
REM Forge Controller - Install Script (Windows)
REM Universal service monitor for managing web services

echo.
echo 🔥 Installing Forge Controller ^(Windows^)...
echo =========================================
echo.

setlocal enabledelayedexpansion

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Install pip dependencies
echo 📦 Installing Python dependencies...
pip install --user PyQt5 requests

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed
echo.

echo ✅ Installation Complete!
echo.
echo 🚀 To start Forge Controller:
echo    python forge_controller.py
echo.
echo 📋 Features:
echo    * Automatically discovers services on ports 80-90 and 8000-9000
echo    * Shows status for each service
echo    * Start, Stop, Restart any service
echo    * View logs
echo    * Open services in browser
echo.
echo 💡 Add to startup:
echo    1. Press Win+R and type: shell:startup
echo    2. Create a shortcut to: python "FULL_PATH_TO_forge_controller.py"
echo.

pause
