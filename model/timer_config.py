import json
import os

class TimerConfig:
    class Timer:
        def __init__(self, key: str, interval: int, is_active: bool = True):
            self.key = key
            self.interval = interval
            self.is_active = is_active

        def to_dict(self):
            return {
                "key": self.key,
                "interval": self.interval,
                "is_active": self.is_active
            }

    def __init__(self, is_running: bool = False, config_path="config.json"):
        self.timer_list = []
        self.is_running = is_running
        self.language = "en"
        self.config_path = config_path
        self.load_config()

    def add_timer(self, key: str, interval: int, is_active: bool = True):
        self.timer_list.append(self.Timer(key, interval, is_active))
        self.save_config()

    def remove_timer(self, key: str):
        self.timer_list = [t for t in self.timer_list if t.key != key]
        self.save_config()

    def toggle_timer(self, key: str):
        for timer in self.timer_list:
            if timer.key == key:
                timer.is_active = not timer.is_active
                self.save_config()
                return timer.is_active
        return False

    def is_timer_active(self, key: str) -> bool:
        for timer in self.timer_list:
            if timer.key == key:
                return timer.is_active
        return False

    def get_language(self):
        return getattr(self, "language", "en")

    def set_language(self, lang_code: str):
        self.language = lang_code
        self.save_config()

    def save_config(self):
        try:
            data = {
                "timers": [t.to_dict() for t in self.timer_list],
                "language": self.language
            }
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

    def load_config(self):
        if not os.path.exists(self.config_path):
            return
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.timer_list = [
                self.Timer(t["key"], t["interval"], t.get("is_active", True))
                for t in data.get("timers", [])
            ]
            self.language = data.get("language", "en")
        except Exception:
            pass
