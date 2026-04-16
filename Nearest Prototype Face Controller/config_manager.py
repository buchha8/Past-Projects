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
                "min_pitch": -30.0,
                "max_pitch": 30.0,
                "min_yaw": -30.0,
                "max_yaw": 0.0
            },
            "keybinds": [
                {
                    "key": "Neutral",
                    "gesture": None,
                    "sensitivity": 1.0,
                    "locked": True
                },
                {
                    "key": "Toggle",
                    "gesture": None,
                    "sensitivity": 1.0,
                    "locked": True
                }
            ]
        }
        self.load_config()
    # -------------------------
    # LOAD / SAVE
    # -------------------------
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

    # -------------------------
    # CORE ACCESS
    # -------------------------
    def get_config(self):
        return self.data

    # -------------------------
    # KEYBIND OPERATIONS
    # -------------------------
    def get_keybinds(self):
        return self.data.get("keybinds", [])

    def add_keybind(self, key, gesture=None, sensitivity=1.0, locked=False):
        keybinds = self.get_keybinds()

        for kb in keybinds:
            if kb["key"] == key:
                raise ValueError(f"Keybind for '{key}' already exists")

        keybinds.append({
            "key": key,
            "gesture": gesture,
            "sensitivity": sensitivity,
            "locked": locked
        })

        self.data["keybinds"] = keybinds

    def delete_keybind(self, index):
        keybinds = self.get_keybinds()

        if index < 0 or index >= len(keybinds):
            return

        if keybinds[index].get("locked", False):
            return

        keybinds.pop(index)
        self.data["keybinds"] = keybinds

    def update_gesture(self, key, gesture):
        for kb in self.get_keybinds():
            if kb["key"] == key:
                kb["gesture"] = gesture
                break

    def update_sensitivity(self, key, sensitivity):
        for kb in self.get_keybinds():
            if kb["key"] == key:
                kb["sensitivity"] = float(sensitivity)
                break

    def get_by_key(self, key):
        for kb in self.get_keybinds():
            if kb["key"] == key:
                return kb
        return None

    # -------------------------
    # CALIBRATION
    # -------------------------
    def set_calibration(self, min_pitch, max_pitch, min_yaw, max_yaw):
        self.data["calibration"] = {
            "min_pitch": min_pitch,
            "max_pitch": max_pitch,
            "min_yaw": min_yaw,
            "max_yaw": max_yaw
        }

    def get_calibration(self):
        return self.data["calibration"]["min_pitch"], self.data["calibration"]["max_pitch"], \
        self.data["calibration"]["min_yaw"], self.data["calibration"]["max_yaw"]   

    # -------------------------
    # MOUSE SPEED
    # -------------------------
    def set_mouse_speed(self, value):
        value = float(value)
        value = max(0.1, min(value, 5.0))
        self.data["mouse_speed"] = value

    def get_mouse_speed(self):
        return self.data.get("mouse_speed", 1.0)

    # -------------------------
    # NORMALIZATION
    # -------------------------
    def _normalize(self):
        if "keybinds" not in self.data or not isinstance(self.data["keybinds"], list):
            self.data["keybinds"] = copy.deepcopy(self.DEFAULT_CONFIG["keybinds"])
        
        # ensure required locked keybinds exist
        existing_keys = {kb["key"] for kb in self.data["keybinds"]}

        for default_kb in self.DEFAULT_CONFIG["keybinds"]:
            if default_kb["key"] not in existing_keys:
                self.data["keybinds"].append(copy.deepcopy(default_kb))

        if "mouse_speed" not in self.data:
            self.data["mouse_speed"] = self.DEFAULT_CONFIG["mouse_speed"]

        if "calibration" not in self.data or not isinstance(self.data["calibration"], dict):
            self.data["calibration"] = self.DEFAULT_CONFIG["calibration"]