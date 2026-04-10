import json
import os

STATE_FILE = "app_state.json"


class AppStateManager:
    def __init__(self):
        self._data = {}

        self.DEFAULT_STATE = {
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

    def load_state(self):
        if not os.path.exists(STATE_FILE):
            self._data = self.DEFAULT_STATE.copy()
            return

        try:
            with open(STATE_FILE, "r") as f:
                self._data = json.load(f)
        except:
            self._data = self.DEFAULT_STATE.copy()

        self._normalize()

    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self._data, f, indent=4)

    def add_state(self, key):
        self._data["keybinds"].append({
            "key": key,
            "gesture": None,
            "sensitivity": 1.0,
            "locked": False
        })

    def delete_state(self, index):
        if 0 <= index < len(self._data.get("keybinds", [])):
            self._data["keybinds"].pop(index)

    def get_state(self):
        return self._data

    def _normalize(self):
        if "keybinds" not in self._data:
            self._data["keybinds"] = self.DEFAULT_STATE["keybinds"]

        if not isinstance(self._data["keybinds"], list):
            self._data["keybinds"] = self.DEFAULT_STATE["keybinds"]