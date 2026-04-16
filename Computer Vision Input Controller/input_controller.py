# =========================================================
# InputController (press/release state machine)
# =========================================================

import pyautogui


class InputController:
    def __init__(self):
        self.active_key = None

    def press_action(self, key):
        if key == "Left Click":
            pyautogui.mouseDown(button="left")
        elif key == "Right Click":
            pyautogui.mouseDown(button="right")
        elif key == "Middle Click":
            pyautogui.mouseDown(button="middle")
        else:
            pyautogui.keyDown(key.lower())

    def release_action(self, key):
        if key == "Left Click":
            pyautogui.mouseUp(button="left")
        elif key == "Right Click":
            pyautogui.mouseUp(button="right")
        elif key == "Middle Click":
            pyautogui.mouseUp(button="middle")
        else:
            pyautogui.keyUp(key.lower())

    def update(self, new_key, enabled):
        if not enabled:
            if self.active_key is not None:
                self.release_action(self.active_key)
                self.active_key = None
            return

        if new_key != self.active_key:
            if self.active_key is not None:
                self.release_action(self.active_key)

            if new_key is not None:
                self.press_action(new_key)

            self.active_key = new_key

    def shutdown(self):
        if self.active_key is not None:
            self.release_action(self.active_key)
            self.active_key = None