import pygetwindow as gw
import pyautogui
import time

# List all open windows with their titles and process IDs
def list_windows():
    windows = []
    for w in gw.getAllWindows():
        if w.title and w.isVisible:
            windows.append({'title': w.title, 'pid': w._hWnd if hasattr(w, '_hWnd') else None})
    return windows

# Focus a window by its title
def focus_window(title):
    win = None
    for w in gw.getAllWindows():
        if w.title == title:
            win = w
            break
    if win:
        win.activate()
        time.sleep(0.1)  # Give time for focus
        return True
    return False

# Send a key to the focused window (use pyautogui)
def send_key_to_window(key):
    pyautogui.press(key)
