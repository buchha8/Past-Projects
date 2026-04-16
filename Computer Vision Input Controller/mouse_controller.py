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

        # -------------------------
        # manual override tracking
        # -------------------------
        self._last_mouse_pos = None
        self._last_manual_time = 0.0
        self._manual_timeout = 2.0

        self.listener = pynput_mouse.Listener(on_move=self._on_mouse_move)
        self.listener.start()

        # -------------------------
        # Kalman filter (state: x, vx, y, vy)
        # -------------------------
        self.state = np.array([
            0.5 * self.screen_width, 0.0,
            0.5 * self.screen_height, 0.0
        ], dtype=float)

        self.P = np.eye(4) * 200.0
        self.I = np.eye(4)

        self.q = 2.0
        self.r = 3000.0

        # -------------------------
        # PID state
        # -------------------------
        self.kp = 0.12
        self.ki = 0.00001
        self.kd = 0.08

        self.max_step = 80.0

        self._last_time = time.time()

        self._ix = 0.0
        self._iy = 0.0

        self._prev_ex = 0.0
        self._prev_ey = 0.0

        self._dex_s = 0.0
        self._dey_s = 0.0

        # -------------------------
        # transition zone
        # -------------------------
        self.exit_deadzone = 50.0
        self.enter_deadzone = 70.0
        self._control_gain = 1.0

    # -------------------------
    # manual override
    # -------------------------
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

    def set_speed(self, speed):
        self.mouse_speed = speed

    def set_enabled(self, enabled):
        self.enabled = enabled

    # -------------------------
    # normalization
    # -------------------------
    def _normalize_centered(self, value, min_val, max_val):
        if value is None or min_val is None or max_val is None:
            return None

        center = 0.5 * (min_val + max_val)
        half_range = 0.5 * (max_val - min_val)

        if abs(half_range) < 1e-6:
            return None

        return (value - center) / half_range

    # -------------------------
    # Kalman filter
    # -------------------------
    def _kalman_update(self, mx, my, dt):
        A = np.array([
            [1, dt, 0,  0],
            [0, 1,  0,  0],
            [0, 0,  1, dt],
            [0, 0,  0, 1]
        ], dtype=float)

        Q = np.array([
            [0.25*dt*dt, 0.5*dt, 0, 0],
            [0.5*dt, dt, 0, 0],
            [0, 0, 0.25*dt*dt, 0.5*dt],
            [0, 0, 0.5*dt, dt]
        ]) * self.q

        x_pred = A @ self.state
        P_pred = A @ self.P @ A.T + Q

        z = np.array([mx, my], dtype=float)

        H = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0]
        ], dtype=float)

        y = z - (H @ x_pred)

        S = H @ P_pred @ H.T + self.r * np.eye(2)

        K = P_pred @ H.T @ np.linalg.inv(S)

        self.state = x_pred + K @ y
        self.P = (self.I - K @ H) @ P_pred

    # -------------------------
    # transition zone hysteresis
    # -------------------------
    def _update_hysteresis(self, ex, ey):
        mag = max(abs(ex), abs(ey))

        if mag <= self.exit_deadzone:
            self._control_gain = 0.0

        elif mag >= self.enter_deadzone:
            self._control_gain = 1.0

        else:
            self._control_gain = (
                (mag - self.exit_deadzone) /
                (self.enter_deadzone - self.exit_deadzone)
            )

        return self._control_gain

    # -------------------------
    # PID
    # -------------------------
    def _pid_step(self, target_x, target_y, dt):
        cx, cy = pyautogui.position()

        ex = target_x - cx
        ey = target_y - cy

        gain = self._update_hysteresis(ex, ey)

        # fade-out instead of hard stop
        if gain <= 0.0:
            self._ix *= 0.95
            self._iy *= 0.95
            return

        self._ix += ex * dt
        self._iy += ey * dt

        self._ix = np.clip(self._ix, -50000, 50000)
        self._iy = np.clip(self._iy, -50000, 50000)

        dex_raw = (ex - self._prev_ex) / max(dt, 1e-3)
        dey_raw = (ey - self._prev_ey) / max(dt, 1e-3)

        alpha = 0.25
        self._dex_s = (1 - alpha) * self._dex_s + alpha * dex_raw
        self._dey_s = (1 - alpha) * self._dey_s + alpha * dey_raw

        self._prev_ex = ex
        self._prev_ey = ey

        dx = (
            self.kp * ex +
            self.ki * self._ix +
            self.kd * self._dex_s
        )

        dy = (
            self.kp * ey +
            self.ki * self._iy +
            self.kd * self._dey_s
        )

        dx = np.clip(dx, -self.max_step, self.max_step)
        dy = np.clip(dy, -self.max_step, self.max_step)

        dx *= self.mouse_speed * gain
        dy *= self.mouse_speed * gain

        pyautogui.moveRel(dx / 5.0, dy / 5.0)

    # -------------------------
    # MAIN LOOP
    # -------------------------
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

        mx = (0.5 + 0.5 * nx) * self.screen_width
        my = (0.5 - 0.5 * ny) * self.screen_height

        now = time.time()
        dt = max(1e-3, now - self._last_time)
        self._last_time = now

        self._kalman_update(mx, my, dt)
        self._pid_step(self.state[0], self.state[2], dt)