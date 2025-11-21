@echo off
REM ForgeWeb - Easy Start Script for Windows
REM This script sets up and starts ForgeWeb automatically

setlocal enabledelayedexpansion

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║                                                       ║
echo ║              🚀  ForgeWeb Startup Wizard  🚀          ║
echo ║                                                       ║
echo ║          Easy Website Builder for GitHub Pages       ║
echo ║                                                       ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python is not installed!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Found Python %PYTHON_VERSION%

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo 📦 Setting up ForgeWeb for the first time...
    echo.
    
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
    
    echo.
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    
    echo.
    echo Upgrading pip...
    python -m pip install --upgrade pip --quiet
    echo ✓ Pip upgraded
    
    echo.
    echo Installing required packages...
    echo   - requests (for API calls^)
    echo   - python-dotenv (for configuration^)
    echo   - pillow (for image processing^)
    pip install requests python-dotenv pillow --quiet
    echo ✓ All packages installed
    
    echo.
    echo Creating project directories...
    if not exist "assets\images" mkdir assets\images
    if not exist "assets\css" mkdir assets\css
    if not exist "assets\js" mkdir assets\js
    if not exist "templates" mkdir templates
    if not exist "uploads" mkdir uploads
    if not exist "user_assets" mkdir user_assets
    echo ✓ Directories created
    
    echo.
    echo Initializing database...
    python admin\database.py
    echo ✓ Database ready
    
    if not exist ".env" (
        echo.
        echo Creating configuration file...
        (
            echo # ForgeWeb Configuration
            echo # You can edit these settings later if needed
            echo.
            echo # Server settings
            echo PORT=8000
            echo HOST=localhost
            echo.
            echo # GitHub Integration (optional - fill in if you want to deploy to GitHub Pages^)
            echo GITHUB_TOKEN=
            echo GITHUB_REPO=
            echo GITHUB_BRANCH=gh-pages
            echo.
            echo # AI Integration (optional - fill in if you want AI writing assistance^)
            echo OPENAI_API_KEY=
            echo ANTHROPIC_API_KEY=
        ) > .env
        echo ✓ Configuration file created (.env^)
    )
    
    echo.
    echo ╔═══════════════════════════════════════════════════════╗
    echo ║                                                       ║
    echo ║              ✨  Setup Complete!  ✨                  ║
    echo ║                                                       ║
    echo ╚═══════════════════════════════════════════════════════╝
    echo.
) else (
    echo ✓ ForgeWeb environment ready
    echo.
    call venv\Scripts\activate.bat
)

REM Check if server is already running
netstat -ano | findstr :8000 | findstr LISTENING >nul 2>nul
if %errorlevel% equ 0 (
    echo ⚠️  Port 8000 is already in use!
    echo.
    echo ForgeWeb server may already be running.
    echo Please close it first or access it at: http://localhost:8000/admin/
    echo.
    pause
    exit /b 0
)

REM Start the server
echo.
echo 🚀 Starting ForgeWeb server...
echo.

if not exist "admin\file-api.py" (
    echo ❌ Error: admin\file-api.py not found!
    echo Make sure you're running this script from the ForgeWeb directory.
    pause
    exit /b 1
)

echo ╔═══════════════════════════════════════════════════════╗
echo ║                                                       ║
echo ║              🎉  ForgeWeb is Running!  🎉             ║
echo ║                                                       ║
echo ╚═══════════════════════════════════════════════════════╝
echo.
echo 📍 Open your web browser and go to:
echo.
echo     http://localhost:8000/admin/
echo.
echo 💡 Tips:
echo   • The admin interface will open where you can build your site
echo   • All changes are saved automatically
echo   • Press Ctrl+C to stop the server when you're done
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

cd admin
python file-api.py

echo.
echo 👋 ForgeWeb server stopped.
echo.
echo To start again, just run: start.bat
echo.
pause
