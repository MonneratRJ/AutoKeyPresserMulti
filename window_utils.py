import pygetwindow as gw
import pyautogui
import time
import sys
import subprocess

# List all open windows with their titles and process IDs
def list_windows():
    windows = []
    if sys.platform == "win32":
        try:
            import win32gui
            import win32process
            import psutil
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        process_name = process.name()
                        windows.append({'hwnd': hwnd, 'title': window_title, 'process': process_name})
                    except:
                        windows.append({'hwnd': hwnd, 'title': window_title, 'process': 'Unknown'})
                return True
            win32gui.EnumWindows(enum_windows_callback, windows)
        except ImportError:
            # fallback to pygetwindow
            for w in gw.getAllWindows():
                if w.title and w.visible:
                    windows.append({'hwnd': getattr(w, '_hWnd', None), 'title': w.title, 'process': 'Unknown'})
    elif sys.platform == "darwin":
        # macOS: use AppleScript
        script = '''
        tell application "System Events"
            set appList to {}
            repeat with theProcess in (every process whose background only is false)
                try
                    set appName to name of theProcess
                    tell theProcess
                        repeat with theWindow in windows
                            set windowName to name of theWindow
                            set end of appList to appName & " - " & windowName
                        end repeat
                    end tell
                end try
            end repeat
            return appList
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.returncode == 0:
            apps = result.stdout.strip().split(', ')
            for i, app in enumerate(apps):
                if app and app != "missing value":
                    windows.append({'id': i, 'title': app, 'process': 'Unknown'})
    else:
        # Linux: use wmctrl
        try:
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line:
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            window_id = parts[0]
                            window_title = parts[3]
                            windows.append({'id': window_id, 'title': window_title, 'process': 'Unknown'})
        except FileNotFoundError:
            pass
    return windows

# Focus a window by its identifier (hwnd for Windows, id for Linux, title for macOS)
def focus_window(window_info):
    if sys.platform == "win32" and 'hwnd' in window_info:
        try:
            import win32gui
            import win32con
            hwnd = window_info['hwnd']
            # Restore if minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            # Bring to foreground
            win32gui.SetForegroundWindow(hwnd)
            # Force window to front if needed
            time.sleep(0.2)
            return True
        except Exception as e:
            print(f"[focus_window] Error: {e}")
            pass
    elif sys.platform == "darwin" and 'title' in window_info:
        app_name = window_info['title'].split(' - ')[0]
        script = f'tell application "{app_name}" to activate'
        subprocess.run(['osascript', '-e', script], capture_output=True)
        time.sleep(0.2)
        return True
    elif sys.platform.startswith("linux") and 'id' in window_info:
        try:
            subprocess.run(['wmctrl', '-ia', window_info['id']], capture_output=True)
            time.sleep(0.2)
            return True
        except FileNotFoundError:
            pass
    return False

# Send a key to the selected window (focuses first, then sends key)
def send_key_to_window(window_info, key):
    focused = focus_window(window_info)
    time.sleep(0.1)
    pyautogui.press(key)
    return focused
