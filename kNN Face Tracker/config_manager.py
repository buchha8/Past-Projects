import json
import os
import copy

CONFIG_FILE = "config.json"


class ConfigManager:
    def __init__(self):
        self.data = {}

        self.DEFAULT_CONFIG = {
            "mouse_speed": 1.0,
            "calibration": {
                "min_pitchyaw": None,
                "max_pitch": None,
                "min_yaw": None,
                "max_yaw": None
            },
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
        if not os.path.exists(CONFIG_FILE):
            self.data = copy.deepcopy(self.DEFAULT_CONFIG)
            return

        try:
            with open(CONFIG_FILE, "r") as f:
                self.data = json.load(f)
        except:
            self.data = copy.deepcopy(self.DEFAULT_CONFIG)

        self._normalize()


    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.data, f, indent=4)


    def add_config(self, key):
        self.data["keybinds"].append({
            "key": key,
            "gesture": None,
            "sensitivity": 1.0,
            "locked": False
        })


    def delete_config(self, index):
        if 0 <= index < len(self.data.get("keybinds", [])):
            self.data["keybinds"].pop(index)


    def get_config(self):
        return self.data


    # -------------------------
    # Calibration
    # -------------------------
    def set_calibration(self, min_pitch, max_pitch, min_yaw, max_yaw):
        self.data["calibration"] = {
            "min_pitch": min_pitch,
            "max_pitch": max_pitch,
            "min_yaw": min_yaw,
            "max_yaw": max_yaw
        }


    def get_calibration(self):
        return self.data.get("calibration", self.DEFAULT_CONFIG["calibration"])
    

    # -------------------------
    # Mouse Speed
    # -------------------------
    def set_mouse_speed(self, value):
        value = float(value)
        value = max(0.1, min(value, 5.0))  # clamp (optional but safe)

        self.data["mouse_speed"] = value


    def get_mouse_speed(self):
        return self.data.get("mouse_speed", 1.0)
    

    # -------------------------
    # Normalization
    # -------------------------
    def _normalize(self):
        if "keybinds" not in self.data or not isinstance(self.data["keybinds"], list):
            self.data["keybinds"] = self.DEFAULT_CONFIG["keybinds"]

        if "mouse_speed" not in self.data:
            self.data["mouse_speed"] = self.DEFAULT_CONFIG["mouse_speed"]

        if "calibration" not in self.data or not isinstance(self.data["calibration"], dict):
            self.data["calibration"] = self.DEFAULT_CONFIG["calibration"]