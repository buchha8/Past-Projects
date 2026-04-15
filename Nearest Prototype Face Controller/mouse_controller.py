import numpy as np
import pyautogui
import time
from pynput import mouse as pynput_mouse


class MouseController:
    def __init__(self, mouse_speed=1.0):
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False

        self.mouse_speed = mouse_speed
        self.enabled = True

        self.vx = 0.0
        self.vy = 0.0

        self.kp = 18.0
        self.kd = 10.0
        self.max_error = 2.5

        self._last_time = time.time()

        self._last_mouse_pos = None
        self._last_manual_time = 0.0
        self._manual_timeout = 2.0

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

        if abs(x - lx) + abs(y - ly) < 3:
            return

        self._last_manual_time = time.time()

    def _manual_override_active(self):
        return (time.time() - self._last_manual_time) < self._manual_timeout

    def _in_deadzone(self, value, min_val, max_val, dz_ratio=0.1):
        if value is None or min_val is None or max_val is None:
            return False

        center = 0.5 * (min_val + max_val)
        half_range = 0.5 * (max_val - min_val)

        if half_range < 1e-6:
            return False

        return abs(value - center) <= (dz_ratio * half_range)

    def _normalize_centered(self, value, min_val, max_val):
        if value is None or min_val is None or max_val is None:
            return None

        if not np.isfinite(value):
            return None

        center = 0.5 * (min_val + max_val)
        half = 0.5 * (max_val - min_val)

        if abs(half) < 1e-6:
            return None

        return (value - center) / half

    def update(self, pitch, yaw, min_pitch, max_pitch, min_yaw, max_yaw, speed=None):
        if speed is not None:
            self.mouse_speed = speed

        if not self.enabled:
            return

        if self._manual_override_active():
            return

        now = time.time()
        dt = now - self._last_time
        self._last_time = now

        if dt <= 0:
            return

        pitch_active = not self._in_deadzone(pitch, min_pitch, max_pitch, 0.6)
        yaw_active = not self._in_deadzone(yaw, min_yaw, max_yaw, 0.6)

        nx = self._normalize_centered(yaw, min_yaw, max_yaw)
        ny = self._normalize_centered(pitch, min_pitch, max_pitch)

        if nx is None or ny is None:
            return

        ex = 0.0
        ey = 0.0

        if yaw_active:
            ex = np.tanh(nx) * self.max_error

        if pitch_active:
            ey = np.tanh(-ny) * self.max_error

        ax = self.kp * ex - self.kd * self.vx
        ay = self.kp * ey - self.kd * self.vy

        self.vx += ax * dt
        self.vy += ay * dt

        dx = self.vx * dt * 100.0 * self.mouse_speed
        dy = self.vy * dt * 100.0 * self.mouse_speed

        max_step = 80.0
        dx = float(np.clip(dx, -max_step, max_step))
        dy = float(np.clip(dy, -max_step, max_step))

        pyautogui.moveRel(dx, dy)