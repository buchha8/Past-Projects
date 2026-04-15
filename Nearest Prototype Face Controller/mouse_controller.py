import numpy as np
import pyautogui
import time
from pynput import mouse as pynput_mouse


class MouseController:
    def __init__(self, mouse_speed=1.0):
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False

        self.screen_width, self.screen_height = pyautogui.size()
        self.mouse_speed = mouse_speed
        self.enabled = True

        # manual override tracking
        self._last_mouse_pos = None
        self._last_manual_time = 0.0
        self._manual_timeout = 2.0

        self.listener = pynput_mouse.Listener(on_move=self._on_mouse_move)
        self.listener.start()

        # -------------------------
        # KALMAN STATE (TARGET SPACE)
        # -------------------------
        self.kx = 0.5 * self.screen_width
        self.ky = 0.5 * self.screen_height
        self.vx_k = 0.0
        self.vy_k = 0.0

        self.px = 1.0
        self.py = 1.0

        self.q_pos = 30.0
        self.q_vel = 20.0
        self.r = 2500.0

        # -------------------------
        # PID STATE (ACTUAL MOTION)
        # -------------------------
        self.x = 0.5 * self.screen_width
        self.y = 0.5 * self.screen_height

        self.vx = 0.0
        self.vy = 0.0

        self.kp = 0.9
        self.max_step = 80.0

        self._last_time = time.time()

    def set_speed(self, speed):
        self.mouse_speed = speed

    def set_enabled(self, enabled):
        self.enabled = enabled

    # -------------------------------------------------
    # MANUAL OVERRIDE
    # -------------------------------------------------
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

    # -------------------------------------------------
    # NORMALIZATION
    # -------------------------------------------------
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

    # -------------------------------------------------
    # KALMAN FILTER (STABLE VERSION)
    # -------------------------------------------------
    def _kalman_update_axis(self, pos, vel, p, meas, dt):
        # prediction
        pos = pos + vel * dt
        p = p + self.q_pos

        # update
        k = p / (p + self.r)
        residual = meas - pos

        pos = pos + k * residual

        # FIXED: no division by dt
        vel = vel + k * residual * 0.1

        p = (1 - k) * p + self.q_vel

        return pos, vel, p

    def _kalman_update(self, mx, my, dt):
        self.kx, self.vx_k, self.px = self._kalman_update_axis(
            self.kx, self.vx_k, self.px, mx, dt
        )
        self.ky, self.vy_k, self.py = self._kalman_update_axis(
            self.ky, self.vy_k, self.py, my, dt
        )

    # -------------------------------------------------
    # PID MOTION
    # -------------------------------------------------
    def _pid_step(self, target_x, target_y, dt):
        ex = target_x - self.x
        ey = target_y - self.y

        damping = 2.2 * np.sqrt(self.kp)

        ax = self.kp * ex - damping * self.vx
        ay = self.kp * ey - damping * self.vy

        self.vx += ax * dt
        self.vy += ay * dt

        step_x = self.vx * dt
        step_y = self.vy * dt

        step_x = float(np.clip(step_x, -self.max_step, self.max_step))
        step_y = float(np.clip(step_y, -self.max_step, self.max_step))

        self.x += step_x
        self.y += step_y

        pyautogui.moveRel(
            step_x * self.mouse_speed,
            step_y * self.mouse_speed
        )

    # -------------------------------------------------
    # MAIN LOOP
    # -------------------------------------------------
    def update(self, pitch, yaw, min_pitch, max_pitch, min_yaw, max_yaw, speed=None):
        if speed is not None:
            self.mouse_speed = speed

        if not self.enabled:
            return

        if self._manual_override_active():
            return

        nx = self._normalize_centered(yaw, min_yaw, max_yaw)
        ny = self._normalize_centered(pitch, min_pitch, max_pitch)

        if nx is None or ny is None:
            return

        screen_x = 0.5 + 0.5 * nx
        screen_y = 0.5 - 0.5 * ny

        mx = screen_x * self.screen_width
        my = screen_y * self.screen_height

        now = time.time()
        dt = max(1e-3, now - self._last_time)
        self._last_time = now

        self._kalman_update(mx, my, dt)
        self._pid_step(self.kx, self.ky, dt)