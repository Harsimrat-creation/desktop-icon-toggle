"""
Desktop Icon Toggle - System Tray App
======================================
Hides/shows desktop icons on double-click.
Runs silently in the system tray.

Requirements:
    pip install pystray pillow pywin32

Run:
    pythonw desktop_icon_toggle.py    (no console window)
    python desktop_icon_toggle.py     (with console, for testing)
"""

import ctypes
import threading
import sys
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw
import pystray
import psutil

# Windows API constants
WM_COMMAND = 0x0111
MOD_ALT = 0x0001
VK_D = 0x44

user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

# Configuration file
CONFIG_FILE = Path.home() / ".desktop_icon_toggle" / "config.json"

# Global state
icons_visible = True


def check_single_instance():
    """Ensure only one instance of this app runs. Kill others if found."""
    current_pid = os.getpid()
    script_name = "desktop_icon_toggle.py"
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and script_name in ' '.join(cmdline):
                if proc.info['pid'] != current_pid:
                    # Found another instance, kill it
                    proc.kill()
                    print(f"Killed duplicate instance (PID: {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def load_config():
    """Load settings from config file."""
    global icons_visible
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                icons_visible = config.get('icons_visible', True)
        except Exception as e:
            print(f"Config load error: {e}")


def save_config():
    """Save settings to config file."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'icons_visible': icons_visible}, f)
    except Exception as e:
        print(f"Config save error: {e}")


def get_desktop_hwnd():
    """Find the hidden ShellDefView window that controls desktop icons."""
    progman = user32.FindWindowW("Progman", None)
    # Send message to spawn WorkerW windows
    user32.SendMessageTimeoutW(progman, 0x052C, 0, 0, 0x0000, 1000, None)

    desktop_hwnd = [None]

    def enum_windows_proc(hwnd, lParam):
        shell_dll_view = user32.FindWindowExW(hwnd, None, "SHELLDLL_DefView", None)
        if shell_dll_view:
            desktop_hwnd[0] = shell_dll_view
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    user32.EnumWindows(EnumWindowsProc(enum_windows_proc), None)

    # Fallback: look inside Progman directly
    if not desktop_hwnd[0]:
        desktop_hwnd[0] = user32.FindWindowExW(progman, None, "SHELLDLL_DefView", None)

    return desktop_hwnd[0]


def set_desktop_icons_visible(visible: bool):
    """Show or hide desktop icons using the Windows Shell API."""
    shell_view = get_desktop_hwnd()
    if not shell_view:
        # Fallback: use registry method
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "HideIcons", 0, winreg.REG_DWORD, 0 if visible else 1)
            # Notify Explorer to refresh
            shell32.SHChangeNotify(0x8000000, 0x1000, None, None)
        except Exception as e:
            print(f"Registry fallback error: {e}")
        return

    # SW_SHOW = 5, SW_HIDE = 0
    show_flag = 5 if visible else 0
    list_view = user32.FindWindowExW(shell_view, None, "SysListView32", None)
    if list_view:
        user32.ShowWindow(list_view, show_flag)


def create_tray_icon_image(visible: bool) -> Image.Image:
    """Create a small icon image reflecting current state."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if visible:
        # Green circle = icons are visible
        draw.ellipse([4, 4, 60, 60], fill=(40, 167, 69, 255))
        # Draw a little grid to represent icons
        for row in range(2):
            for col in range(2):
                x = 16 + col * 18
                y = 16 + row * 18
                draw.rectangle([x, y, x + 12, y + 12], fill=(255, 255, 255, 200))
    else:
        # Gray circle = icons are hidden
        draw.ellipse([4, 4, 60, 60], fill=(108, 117, 125, 255))
        # Draw an X
        draw.line([20, 20, 44, 44], fill=(255, 255, 255, 220), width=5)
        draw.line([44, 20, 20, 44], fill=(255, 255, 255, 220), width=5)

    return img


def toggle_icons(icon, item=None):
    """Toggle desktop icon visibility."""
    global icons_visible
    icons_visible = not icons_visible
    set_desktop_icons_visible(icons_visible)
    save_config()
    update_tray(icon)


def update_tray(icon):
    """Update tray icon and tooltip to reflect current state."""
    icon.icon = create_tray_icon_image(icons_visible)
    icon.title = (
        "Desktop Icons: VISIBLE\nDouble-click to hide"
        if icons_visible
        else "Desktop Icons: HIDDEN\nDouble-click to show"
    )


def on_double_click(icon, button):
    """Handle double-click on tray icon."""
    # pystray fires left-click; we use this as our toggle trigger
    toggle_icons(icon)


def quit_app(icon, item):
    """Restore icons before quitting."""
    if not icons_visible:
        set_desktop_icons_visible(True)
    icon.stop()


def setup_autostart(enable: bool):
    """Add or remove this script from Windows startup."""
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "DesktopIconToggle"
    exe_path = f'pythonw "{sys.argv[0]}"'

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
    except Exception as e:
        print(f"Autostart error: {e}")


def main():
    global icons_visible

    # Ensure only one instance runs
    check_single_instance()

    # Load saved configuration
    load_config()
    
    # Enable autostart by default
    setup_autostart(True)
    
    set_desktop_icons_visible(icons_visible)

    # Build tray icon
    image = create_tray_icon_image(icons_visible)

    menu = pystray.Menu(
        pystray.MenuItem("Show / Hide Icons", toggle_icons, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Disable autostart on login", lambda icon, item: setup_autostart(False)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit (restores icons)", quit_app),
    )

    icon = pystray.Icon(
        name="DesktopIconToggle",
        icon=image,
        title="Desktop Icons: HIDDEN\nDouble-click to show" if not icons_visible else "Desktop Icons: VISIBLE\nDouble-click to hide",
        menu=menu,
    )

    # Double-click = toggle
    icon.on_double_click = on_double_click

    icon.run()


if __name__ == "__main__":
    main()
