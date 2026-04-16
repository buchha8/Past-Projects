import cv2
import gestures
import landmarks
import time
from PySide6.QtCore import QObject, QTimer


class AppOrchestrator(QObject):

    def __init__(self, config, window, mouse, gesture_processor, input):
        super().__init__()

        self.config = config
        self.window = window
        self.mouse = mouse
        self.gesture_processor = gesture_processor
        self.input = input

        # -------------------------
        # Vision
        # -------------------------
        self.cap = cv2.VideoCapture(0)
        self.landmarker = landmarks.create_landmarker()
        self.blendshape_order = None
        self.current_blendshapes = None
        self.current_roll = None
        self.current_pitch = None
        self.current_yaw = None

        # -------------------------
        # Calibration
        # -------------------------
        self.min_pitch, self.max_pitch, self.min_yaw, self.max_yaw = self.config.get_calibration()
        self.mouse.set_speed(self.config.get_mouse_speed())

        # -------------------------
        # UI wiring
        # -------------------------
        self.window.add_keybind_requested.connect(self.on_add_keybind)
        self.window.delete_keybind_requested.connect(self.on_delete_keybind)
        self.window.edit_gesture_requested.connect(self.on_edit_gesture)
        self.window.calibrate_requested.connect(self.on_calibrate)
        self.window.mouse_speed_changed.connect(self.on_mouse_speed_changed)
        self.window.edit_sensitivity_requested.connect(self.on_edit_sensitivity)
        self.window.closed.connect(self.shutdown)
        self.window.disable_gestures_changed.connect(self.on_disable_gestures_changed)
        self.window.disable_mouse_changed.connect(self.on_disable_mouse_changed)

        self.window.update_table(self.config.get_keybinds())
        self.window.mouse_speed_slider.setValue(int(self.config.get_mouse_speed() * 10))
        self.disable_gestures = False
        self.disable_mouse = False

        # -------------------------
        # Loop
        # -------------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_frame)
        self.timer.start(30)

    # =========================================================
    # FRAME LOOP
    # =========================================================
    def on_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return True

        # -------------------------
        # Landmarks pipeline
        # -------------------------
        timestamp_ms = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
        results = landmarks.detect_face_data(frame, self.landmarker, timestamp_ms)
        display, self.current_roll, self.current_pitch, self.current_yaw = landmarks.process_landmarks_pipeline(results, frame)

        # -------------------------
        # Gesture pipeline (optional)
        # -------------------------
        stable = None
        new_key = None
        enabled = False
        gesture = None

        if not self.disable_gestures:
            self.current_blendshapes = landmarks.extract_blendshape_vector(results)

            if self.current_blendshapes and self.blendshape_order is None:
                self.blendshape_order = gestures.initialize_order(self.current_blendshapes)

            gesture = gestures.compute_gesture(
                self.current_blendshapes,
                self.config.get_config(),
                self.blendshape_order
            )

        result = self.gesture_processor.update(gesture)

        stable = result["stable"]
        new_key = result["key"]
        enabled = result["enabled"]

        # -------------------------
        # FINAL CONTROL SIGNALS
        # -------------------------
        input_allowed = (not self.disable_gestures) and enabled
        mouse_allowed = (not self.disable_mouse) and enabled

        # -------------------------
        # Input handling
        # -------------------------
        if input_allowed:
            self.input.update(new_key, True)
        else:
            self.input.update(None, False)

        # -------------------------
        # Mouse control
        # -------------------------
        if mouse_allowed and self._calibration_valid():
            self.mouse.update(
                self.current_pitch,
                self.current_yaw,
                self.min_pitch,
                self.max_pitch,
                self.min_yaw,
                self.max_yaw,
            )

        # -------------------------
        # UI
        # -------------------------
        if stable is not None:
            self.window.update_gesture(stable["name"])
        else:
            self.window.update_gesture(None)

        self.window.update_head_angles(
            self.current_roll,
            self.current_pitch,
            self.current_yaw
        )

        self.window.update_landmarks(display)
        self.window.update_toggle(enabled)

        return True

    # =========================================================
    # UI HANDLERS
    # =========================================================
    def on_add_keybind(self, key):
        try:
            self.config.add_keybind(key)
            self.config.save_config()
            self.window.update_table(self.config.get_keybinds())
        except ValueError:
            pass

    def on_delete_keybind(self, row):
        self.config.delete_keybind(row)
        self.config.save_config()
        self.window.update_table(self.config.get_keybinds())

    def on_edit_gesture(self, row, name):
        keybinds = self.config.get_keybinds()
        key = keybinds[row]["key"]

        gesture_data = {
            "name": name,
            "blendshapes": self.current_blendshapes
        }

        self.config.update_gesture(key, gesture_data)
        self.config.save_config()
        self.window.update_table(self.config.get_keybinds())

    def on_edit_sensitivity(self, row, value):
        keybinds = self.config.get_keybinds()
        key = keybinds[row]["key"]

        self.config.update_sensitivity(key, value)
        self.config.save_config()
        self.window.update_table(self.config.get_keybinds())

    def on_calibrate(self, step_index):
        if self.current_pitch is None or self.current_yaw is None:
            return

        if step_index == 0:
            self.min_pitch = float(self.current_pitch)
        elif step_index == 1:
            self.max_pitch = float(self.current_pitch)
        elif step_index == 2:
            self.min_yaw = float(self.current_yaw)
        elif step_index == 3:
            self.max_yaw = float(self.current_yaw)

            self.config.set_calibration(
                self.min_pitch,
                self.max_pitch,
                self.min_yaw,
                self.max_yaw,
            )
            self.config.save_config()

    def on_mouse_speed_changed(self, speed):
        self.mouse.set_speed(speed)
        self.config.set_mouse_speed(speed)
        self.config.save_config()

    def on_disable_gestures_changed(self, value):
        self.disable_gestures = value

        if value:
            self.input.update(None, False)

    def on_disable_mouse_changed(self, value):
        self.disable_mouse = value

    # =========================================================
    # LIFECYCLE
    # =========================================================
    def shutdown(self):
        if self.timer.isActive():
            self.timer.stop()

        if self.cap:
            self.cap.release()
            self.cap = None

        self.input.shutdown()

    # =========================================================
    # UTIL
    # =========================================================
    def _calibration_valid(self):
        return (
            self.min_pitch is not None and
            self.max_pitch is not None and
            self.min_yaw is not None and
            self.max_yaw is not None and
            self.max_pitch > self.min_pitch and
            self.max_yaw > self.min_yaw
        )