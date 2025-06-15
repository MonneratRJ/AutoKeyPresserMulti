import os
import sys
import webview
import logging
import json
from model.timer_config import TimerConfig
from controller.timer_controller import TimerController
from model.i18n_manager import I18nManager

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')

class API:
    def __init__(self, timer_config, timer_controller, i18n_manager):
        self.timer_config = timer_config
        self.timer_controller = timer_controller
        self.i18n_manager = i18n_manager
        # Load language from config if present
        lang = self.timer_config.get_language()
        if lang:
            self.i18n_manager.set_language(lang)
            self.current_language = lang
        else:
            self.current_language = "en"  # Default language

    def get_translations(self):
        try:
            return {
                "app_title": self.i18n_manager.get_text("app_title"),
                "start": self.i18n_manager.get_text("start"),
                "stop": self.i18n_manager.get_text("stop"),
                "add": self.i18n_manager.get_text("add"),
                "remove": self.i18n_manager.get_text("remove"),
                "language": self.i18n_manager.get_text("language"),
                "error": self.i18n_manager.get_text("error"),
                "success": self.i18n_manager.get_text("success"),
                "active": self.i18n_manager.get_text("active"),
                "key": self.i18n_manager.get_text("key"),
                "interval": self.i18n_manager.get_text("interval"),
                "actions": self.i18n_manager.get_text("actions")
            }
        except Exception as e:
            logging.error(f"Error getting translations: {str(e)}")
            return {}

    def set_language(self, lang_code):
        try:
            self.i18n_manager.set_language(lang_code)
            self.current_language = lang_code
            self.timer_config.set_language(lang_code)  # Persist language
            logging.info(f"Language changed to: {lang_code}")
            return True
        except Exception as e:
            logging.error(f"Error setting language: {str(e)}")
            return False

    def get_available_languages(self):
        try:
            return self.i18n_manager.get_available_languages()
        except Exception as e:
            logging.error(f"Error getting available languages: {str(e)}")
            return ["en"]

    def get_timers(self):
        try:
            timers = [{"key": t.key, "interval": t.interval, "is_active": t.is_active} 
                     for t in self.timer_config.timer_list]
            logging.info(f"Retrieved timers: {timers}")
            return timers
        except Exception as e:
            logging.error(f"Error getting timers: {str(e)}")
            return []

    def start_timers(self):
        try:
            self.timer_controller.start_timers()
            logging.info("Starting timers...")
            return True
        except Exception as e:
            logging.error(f"Error starting timers: {str(e)}")
            return False

    def stop_timers(self):
        try:
            self.timer_controller.stop_timers()
            logging.info("Stopping timers...")
            return True
        except Exception as e:
            logging.error(f"Error stopping timers: {str(e)}")
            return False

    def add_timer(self, key, interval):
        try:
            self.timer_config.add_timer(key, int(interval))
            logging.info(f"Added timer: key={key}, interval={interval}")
            return True
        except Exception as e:
            logging.error(f"Error adding timer: {str(e)}")
            return False

    def remove_timer(self, key):
        try:
            self.timer_config.remove_timer(key)
            logging.info(f"Removed timer: key={key}")
            return True
        except Exception as e:
            logging.error(f"Error removing timer: {str(e)}")
            return False

    def toggle_timer(self, key):
        try:
            is_active = self.timer_config.toggle_timer(key)
            logging.info(f"Toggled timer: key={key}, is_active={is_active}")
            return True
        except Exception as e:
            logging.error(f"Error toggling timer: {str(e)}")
            return False

    def debug(self, message):
        logging.info(f"Debug from JS: {message}")

class TimerUI:
    def __init__(self):
        self.timer_config = TimerConfig()
        self.timer_controller = TimerController(self.timer_config)
        self.i18n_manager = I18nManager()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.window = None
        self.api = API(self.timer_config, self.timer_controller, self.i18n_manager)
        logging.info("UI initialized")

    def start(self):
        try:
            self.window = webview.create_window(
                self.i18n_manager.get_text("app_title"),
                url=self._get_resource_path('index.html'),
                js_api=self.api,
                min_size=(400, 300)
            )
            webview.start(debug=False)
            logging.info("Window created successfully")
        except Exception as e:
            logging.error(f"Error starting UI: {str(e)}")
            raise

    def _get_resource_path(self, filename):
        return os.path.join(self.current_dir, filename)

if __name__ == "__main__":
    ui = TimerUI()
    ui.start()
