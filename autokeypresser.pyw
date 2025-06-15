import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from views.ui import TimerUI

    if __name__ == "__main__":
        try:
            ui = TimerUI()
            ui.start()  # Run UI on main thread (required by pywebview)
        except Exception as e:
            raise
except Exception as e:
    raise