import numpy as np
import pyautogui
import time
from pynput import mouse as pynput_mouse


class MouseController:
    def __init__(self, mouse_speed=1.0):
        pyautogui.PAUSE = 0

        self.screen_width, self.screen_height = pyautogui.size()
        self.mouse_speed = mouse_speed

        self.enabled = True

        # manual override state
        self._last_mouse_pos = None
        self._last_manual_time = 0.0
        self._manual_timeout = 0.5

        self.listener = pynput_mouse.Listener(on_move=self._on_mouse_move)
        self.listener.start()

    def set_speed(self, speed):
        self.mouse_speed = speed

    def set_enabled(self, enabled):
        self.enabled = enabled

    def _on_mouse_move(self, x, y):
        if self._last_mouse_pos is None:
            self._last_mouse_pos = (x, y)
            return

        lx, ly = self._last_mouse_pos
        self._last_mouse_pos = (x, y)

        dx = x - lx
        dy = y - ly

        if abs(dx) + abs(dy) < 3:
            return

        self._last_manual_time = time.time()

    def _manual_override_active(self):
        return (time.time() - self._last_manual_time) < self._manual_timeout

    def _normalize_centered(self, value, min_val, max_val):
        if value is None or min_val is None or max_val is None:
            return None

        if not np.isfinite(value):
            return None

        center = 0.5 * (min_val + max_val)
        half_range = 0.5 * (max_val - min_val)

        if abs(half_range) < 1e-6:
            return None

        return (value - center) / half_range

    def update(self, pitch, yaw, min_pitch, max_pitch, min_yaw, max_yaw, speed=None):
        if speed is not None:
            self.mouse_speed = speed

        # hard gates
        if not self.enabled:
            return

        if self._manual_override_active():
            return

        nx = self._normalize_centered(yaw, min_yaw, max_yaw)
        ny = self._normalize_centered(pitch, min_pitch, max_pitch)

        if nx is None or ny is None:
            return

        nx *= self.mouse_speed
        ny *= self.mouse_speed

        screen_x = 0.5 + 0.5 * nx
        screen_y = 0.5 - 0.5 * ny

        screen_x = float(np.clip(screen_x, 0.0, 1.0))
        screen_y = float(np.clip(screen_y, 0.0, 1.0))

        px = int(screen_x * self.screen_width)
        py = int(screen_y * self.screen_height)

        pyautogui.moveTo(px, py)