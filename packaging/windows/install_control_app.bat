@echo off
REM Install Windows Dashboard Control App

echo.
echo 🍕 Installing Dashboard Controller for Windows...
echo ====================================

REM Find dashboard directory
for %%f in (%~dp0..) do set "DASHBOARD_DIR=%%~ff"
for %%f in ("%DASHBOARD_DIR%") do set "DASHBOARD_DIR=%%~ff"

echo Dashboard directory: %DASHBOARD_DIR%

REM Install PyQt5 and requests
echo.
echo 📦 Installing Python dependencies...
pip install PyQt5 requests --quiet

echo ✅ Dependencies installed

REM Copy logo if it exists
if exist "%DASHBOARD_DIR%\assets\images\forge-logo.png" (
    echo 📁 Copying forge logo...
    copy "%DASHBOARD_DIR%\assets\images\forge-logo.png" "%~dp0forge-logo.png" >nul
    echo ✅ Logo copied to installer directory
)

echo.
echo ✅ Installation complete!
echo.
echo 🚀 To run:
echo    python dashboard_control.py
echo.
echo 🔇 To run in background (no console window):
echo    pythonw dashboard_control.py
echo.
echo 🔧 To add to startup:
echo    1. Press Win+R
echo    2. Type: shell:startup
echo    3. Create shortcut to dashboard_control.py in that folder
echo.
pause
