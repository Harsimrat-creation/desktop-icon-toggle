@echo off
echo ============================================
echo   Desktop Icon Toggle - Setup & Run
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Stopping any existing instances...
taskkill /F /IM pythonw.exe 2>nul
timeout /t 1 >nul

echo [2/4] Installing required packages...
pip install pystray pillow pywin32 psutil --quiet

echo [3/4] Setting up autostart...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_startup_shortcut.ps1" 2>nul

echo [4/4] Starting Desktop Icon Toggle...
echo.
echo The app will run in your system tray (bottom-right corner).
echo Double-click the tray icon to toggle desktop icons.
echo Right-click for more options (disable autostart, quit).
echo.
echo Your current icon state will be remembered next time you start.
echo.

REM Run without a console window (pythonw)
start "" pythonw "%~dp0desktop_icon_toggle.py"

echo App started! Check your system tray.
timeout /t 3 >nul
