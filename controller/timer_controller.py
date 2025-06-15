import threading
import time
import logging
from model.timer_config import TimerConfig

class TimerController:
    def __init__(self, timer_config: TimerConfig):
        self.timer_config = timer_config
        self.threads = {}
        self.running = False
        logging.info("TimerController (threading) initialized")

    def _timer_action(self, key, interval):
        while self.running and self.timer_config.is_timer_active(key):
            self._press_key(key)
            time.sleep(interval / 1000.0)

    def start_timers(self):
        self.running = True
        for timer in self.timer_config.timer_list:
            if timer.is_active and timer.key not in self.threads:
                t = threading.Thread(target=self._timer_action, args=(timer.key, timer.interval), daemon=True)
                self.threads[timer.key] = t
                t.start()
                logging.info(f"Started thread for key {timer.key}")
        logging.info(f"Scheduled {len(self.threads)} timer threads.")

    def stop_timers(self):
        logging.info("Stopping all timers (threading)")
        self.running = False
        self.threads.clear()
        logging.info("All timers stopped (threading)")

    def _press_key(self, key):
        try:
            import pyautogui
            pyautogui.press(key)
        except Exception:
            pass  # Fail silently if keypress fails
