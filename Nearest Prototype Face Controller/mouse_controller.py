import numpy as np
import pyautogui


class MouseController:
    def __init__(self, mouse_speed=1.0):
        pyautogui.PAUSE = 0

        self.screen_width, self.screen_height = pyautogui.size()

        self.mouse_speed = mouse_speed

        self.x = 0.5
        self.y = 0.5

        self.vx = 0.0
        self.vy = 0.0

        self.smoothing = 0.88

        self.yaw_sensitivity = 0.02
        self.pitch_sensitivity = 0.02

        self._initialized = False

    def set_speed(self, speed):
        self.mouse_speed = speed

    def _project(self, pitch, yaw):
        if pitch is None or yaw is None:
            return None

        if not np.isfinite(pitch) or not np.isfinite(yaw):
            return None

        # unbounded linear projection (NO CLAMP HERE)
        x = yaw * self.yaw_sensitivity
        y = pitch * self.pitch_sensitivity

        return x, y

    def update(self, pitch, yaw, min_pitch, max_pitch, min_yaw, max_yaw, speed=None):
        if speed is not None:
            self.mouse_speed = speed

        target = self._project(pitch, yaw)

        if target is None:
            return

        tx, ty = target

        if not self._initialized:
            self.x = tx
            self.y = ty
            self._initialized = True
            return

        self.x = self.x * self.smoothing + tx * (1.0 - self.smoothing)
        self.y = self.y * self.smoothing + ty * (1.0 - self.smoothing)

        screen_x = 0.5 + self.x

        # FIX: invert pitch direction
        screen_y = 0.5 - self.y

        screen_x = float(np.clip(screen_x, 0.0, 1.0))
        screen_y = float(np.clip(screen_y, 0.0, 1.0))

        px = int(screen_x * self.screen_width)
        py = int(screen_y * self.screen_height)

        pyautogui.moveTo(px, py)