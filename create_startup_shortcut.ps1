# Create a shortcut for autostart
$WshShell = New-Object -ComObject WScript.Shell
$ShortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\DesktopIconToggle.lnk"
$ScriptPath = $PSScriptRoot + "\desktop_icon_toggle.py"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "pythonw"
$Shortcut.Arguments = """$ScriptPath"""
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.WindowStyle = 7  # Hidden window
$Shortcut.IconLocation = "shell32.dll, 44"
$Shortcut.Save()

Write-Host "Autostart shortcut created: $ShortcutPath"
