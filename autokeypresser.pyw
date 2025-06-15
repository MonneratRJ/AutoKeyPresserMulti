import sys
import os
import logging

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from views.ui import TimerUI
    logging.info("Successfully imported TimerUI")
    
    if __name__ == "__main__":
        try:
            ui = TimerUI()
            ui.start()  # Run UI on main thread (required by pywebview)
        except Exception as e:
            logging.error(f"Error in main: {str(e)}")
            raise
except Exception as e:
    logging.error(f"Import error: {str(e)}")
    raise