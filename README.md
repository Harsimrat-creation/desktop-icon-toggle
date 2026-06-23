# 🛡 Desktop Icon Toggle

> Hide your desktop data from prying eyes — instantly.

A lightweight Windows system tray app that hides or shows all desktop icons
with one double-click. Perfect for screen sharing, meetings, streaming, and
keeping your files private.

## ✨ Features
- One-click toggle from the system tray
- Remembers your last state across restarts
- Auto-starts with Windows (optional)
- No internet connection, no data collected
- No admin rights required
- Open source — MIT licensed

## 📥 Download
👉 [Download the latest release](https://github.com/YOURUSERNAME/desktop-icon-toggle/releases/latest)

## 🚀 Run from source (requires Python)
```bash
pip install pystray pillow pywin32 psutil
pythonw desktop_icon_toggle.py
```
Or just double-click `run_app.bat` — it installs everything automatically.

## 🖥 Requirements
- Windows 10 or 11 (64-bit)
- Python 3.8+ (only if running from source)

## 📁 Files
| File | Purpose |
|---|---|
| `desktop_icon_toggle.py` | Main app logic |
| `run_app.bat` | Install deps + launch app |
| `setup_startup.bat` | Create Windows startup shortcut |
| `create_startup_shortcut.ps1` | PowerShell shortcut helper |

## 🔒 Privacy & Security
- Zero network calls — works fully offline
- Files are never deleted or modified — icons are just hidden
- Uses the official Windows Shell API (`SysListView32`)
- Fully auditable — read every line on GitHub

## 📄 License
MIT — free to use, modify, and distribute.


##⚠️ Windows SmartScreen may show a warning because this is a newly released application and does not yet have a reputation history. The application runs locally and does not collect or transmit user data.


