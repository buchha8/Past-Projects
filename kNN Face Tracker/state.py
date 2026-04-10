import json
import os

STATE_FILE = "state.json"

DEFAULT_STATE = {
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

state = {}

def load_state():
    global state
    
    if not os.path.exists("state.json"):
        state = DEFAULT_STATE.copy()
        return

    try:
        with open("state.json", "r") as f:
            state = json.load(f)
    except:
        state = DEFAULT_STATE.copy()


def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


def add_state(key):
    state["keybinds"].append({
        "key": key,
        "gesture": None,
        "sensitivity": 1.0
    })


def delete_state(index):
    if index <= 0:
        return
    if index < len(state["keybinds"]):
        state["keybinds"].pop(index)