import json
import os

STATE_FILE = "app_state.json"


class AppStateManager:
    def __init__(self):
        self.state = {}

        self.DEFAULT_STATE = {
            "enabled": True,
            "mouse_speed": 1.0,
            "keybinds": [
                {
                    "key": "Toggle",
                    "gesture": None,
                    "sensitivity": 1.0
                }
            ]
        }

    def load_state(self):
        if not os.path.exists(STATE_FILE):
            self.state = self.DEFAULT_STATE.copy()
            return

        try:
            with open(STATE_FILE, "r") as f:
                self.state = json.load(f)
        except:
            self.state = self.DEFAULT_STATE.copy()

        self._normalize()

    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=4)

    def add_state(self, key):
        self.state["keybinds"].append({
            "key": key,
            "gesture": None,
            "sensitivity": 1.0
        })

    def delete_state(self, index):
        if 0 <= index < len(self.state.get("keybinds", [])):
            self.state["keybinds"].pop(index)

    def get_state(self):
        return self.state

    def _normalize(self):
        if "keybinds" not in self.state:
            self.state["keybinds"] = self.DEFAULT_STATE["keybinds"]

        if not isinstance(self.state["keybinds"], list):
            self.state["keybinds"] = self.DEFAULT_STATE["keybinds"]