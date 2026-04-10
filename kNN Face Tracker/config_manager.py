import json
import os

config_FILE = "config.json"


class ConfigManager:
    def __init__(self):
        self._data = {}

        self.DEFAULT_CONFIG = {
            "enabled": True,
            "mouse_speed": 1.0,
            "keybinds": [
                {
                    "key": "Toggle",
                    "gesture": None,
                    "sensitivity": 1.0,
                    "locked": True
                }
            ]
        }

    def load_config(self):
        if not os.path.exists(config_FILE):
            self._data = self.DEFAULT_CONFIG.copy()
            return

        try:
            with open(config_FILE, "r") as f:
                self._data = json.load(f)
        except:
            self._data = self.DEFAULT_CONFIG.copy()

        self._normalize()

    def save_config(self):
        with open(config_FILE, "w") as f:
            json.dump(self._data, f, indent=4)

    def add_config(self, key):
        self._data["keybinds"].append({
            "key": key,
            "gesture": None,
            "sensitivity": 1.0,
            "locked": False
        })

    def delete_config(self, index):
        if 0 <= index < len(self._data.get("keybinds", [])):
            self._data["keybinds"].pop(index)

    def get_config(self):
        return self._data

    def _normalize(self):
        if "keybinds" not in self._data:
            self._data["keybinds"] = self.DEFAULT_CONFIG["keybinds"]

        if not isinstance(self._data["keybinds"], list):
            self._data["keybinds"] = self.DEFAULT_CONFIG["keybinds"]