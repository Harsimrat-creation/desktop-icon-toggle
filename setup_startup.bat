@echo off
echo ============================================
echo  Desktop Icon Toggle - Setup Startup
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

echo Installing required packages...
pip install pystray pillow pywin32 --quiet

echo.
echo Creating startup shortcut...

REM Get the current directory
set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%desktop_icon_toggle.py

REM Create a VBScript to create the shortcut (Windows Registry method)
setlocal enabledelayedexpansion
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Create a simple PowerShell script to create the shortcut
powershell -NoProfile -Command "^
$WshShell = New-Object -ComObject WScript.Shell; ^
$ShortcutPath = '%STARTUP_DIR%\DesktopIconToggle.lnk'; ^
$Shortcut = $WshShell.CreateShortcut($ShortcutPath); ^
$Shortcut.TargetPath = 'pythonw'; ^
$Shortcut.Arguments = '%SCRIPT_PATH%'; ^
$Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; ^
$Shortcut.WindowStyle = 7; ^
$Shortcut.IconLocation = 'shell32.dll, 44'; ^
$Shortcut.Save(); ^
Write-Host 'Shortcut created: ' $ShortcutPath"

echo.
echo Setup complete!
echo The app will now start automatically when you log in.
echo You can manage startup from the system tray menu.
echo.
timeout /t 3 >nul
