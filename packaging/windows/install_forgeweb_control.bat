@echo off
REM Install ForgeWeb Control App (Windows)
REM Smart installer that integrates with existing Dashboard controller or installs standalone

echo.
echo 🍕 Installing ForgeWeb Control App (Windows)...
echo ================================================

REM Find ForgeWeb directory
for %%f in (%~dp0.) do set "PACKAGING_DIR=%%~ff"
for %%f in ("%PACKAGING_DIR%..") do set "FORGEWEB_DIR=%%~ff"

echo ForgeWeb directory: %FORGEWEB_DIR%

REM Verify ForgeWeb structure
if not exist "%FORGEWEB_DIR%\start.bat" (
    if not exist "%FORGEWEB_DIR%\start.sh" (
        echo ❌ Error: ForgeWeb not found at %FORGEWEB_DIR%
        echo    Make sure you're running this from packaging\windows\
        pause
        exit /b 1
    )
)

echo ✅ ForgeWeb found

echo.
echo 🔍 Checking for existing Dashboard controller...

REM Check if Dashboard controller is installed
set "DASHBOARD_EXISTS=0"
if exist "%PACKAGING_DIR%\windows\dashboard_control.py" (
    set "DASHBOARD_EXISTS=1"
    echo ✅ Dashboard controller app found
)

REM Determine installation mode
if %DASHBOARD_EXISTS% equ 1 (
    echo 📦 Integration Mode: Adding ForgeWeb to existing Dashboard controller
    set "MODE=integrated"
) else (
    echo 📦 Installation Mode: Installing ForgeWeb as standalone controller
    set "MODE=standalone"
)

echo.
echo 📦 Installing Python dependencies...

REM Install PyQt5 and requests
pip install PyQt5 requests --quiet

echo ✅ Dependencies installed
echo.

REM Copy logo if it exists
if exist "%FORGEWEB_DIR%\packaging\macos\forge-logo.png" (
    echo 📁 Copying forge logo...
    copy "%FORGEWEB_DIR%\packaging\macos\forge-logo.png" "%~dp0forge-logo.png" >nul
    echo ✅ Logo copied to installer directory
)

if exist "%FORGEWEB_DIR%\packaging\macos\buildly_icon.png" (
    echo 📁 Copying Buildly icon...
    copy "%FORGEWEB_DIR%\packaging\macos\buildly_icon.png" "%~dp0buildly_icon.png" >nul
    echo ✅ Icon copied to installer directory
)

echo.
echo ✅ Installation complete!
echo.
echo 🚀 To run:
echo    python forgeweb_control.py
echo.
echo 🔇 To run in background (no console window):
echo    pythonw forgeweb_control.py
echo.
echo 🔧 To add to startup:
echo    1. Press Win+R
echo    2. Type: shell:startup
echo    3. Create shortcut to forgeweb_control.py in that folder
echo.

if "%MODE%"=="integrated" (
    echo 🔗 Integration Mode:
    echo    ForgeWeb controls will be added to your existing Dashboard controller
    echo.
) else (
    echo 🔧 Standalone Mode:
    echo    ForgeWeb will run as a separate controller
    echo.
)

echo ℹ️  Configuration saved to: %FORGEWEB_DIR%\.forgeweb_control_config.json
echo.
echo 📚 For more help, see: %~dp0FORGEWEB_CONTROL_README.md
echo.

pause
