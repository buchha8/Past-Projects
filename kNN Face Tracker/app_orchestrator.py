import cv2
import gestures
import landmarks
import pyautogui
import time
from PySide6.QtCore import QObject, QTimer


class AppOrchestrator(QObject):

    def __init__(self, config, window):
        super().__init__()

        self.config = config
        self.window = window

        # Camera / vision pipeline
        self.cap = cv2.VideoCapture(0)
        self.landmarker = landmarks.create_landmarker()

        # -------------------------
        # OTHER INITS
        # -------------------------
        self.blendshape_order = None
        self.current_blendshapes = None
        self.current_roll = None
        self.current_pitch = None
        self.current_yaw = None
        self.active_key = None
        self.enabled = True
        self.toggle_start_time = None
        self.toggle_triggered = False

        # -------------------------
        # CONNECT UI SIGNALS
        # -------------------------
        self.window.add_keybind_requested.connect(self.on_add_keybind)
        self.window.delete_keybind_requested.connect(self.on_delete_keybind)
        self.window.edit_gesture_requested.connect(self.on_edit_gesture)
        self.window.calibrate_requested.connect(self.on_calibrate)
        self.window.mouse_speed_changed.connect(self.on_mouse_speed_changed)
        self.window.edit_sensitivity_requested.connect(self.on_edit_sensitivity)
        self.window.closed.connect(self.shutdown)

        # -------------------------
        # INITIAL UI SYNC
        # -------------------------
        self.window.update_table(self.config.get_keybinds())
        self.window.mouse_speed_slider.setValue(int(self.config.get_mouse_speed() * 10))
        # -------------------------
        # FRAME LOOP
        # -------------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_frame)
        self.timer.start(30)

    # -------------------------
    # FRAME LOOP
    # -------------------------
    def on_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return True

        timestamp_ms = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
        results = landmarks.detect_face_data(frame, self.landmarker, timestamp_ms)
        self.current_blendshapes = landmarks.extract_blendshape_vector(results)
        if self.current_blendshapes and self.blendshape_order is None:
            self.blendshape_order = gestures.initialize_order(self.current_blendshapes)

        landmarks_pixels = landmarks.extract_landmarks_pixels(results, frame)
        transform_matrix = landmarks.extract_transform_matrix(results)

        self.current_roll, self.current_pitch, self.current_yaw = landmarks.compute_head_pose_angles(transform_matrix)

        centered = landmarks.compute_landmarks_centered(landmarks_pixels)
        normalized = landmarks.compute_landmarks_normalized(landmarks_pixels, centered)
        display = landmarks.compute_landmarks_display(normalized)

        gesture = gestures.compute_gesture(self.current_blendshapes, self.config.get_config(), self.blendshape_order)
        self._process_gesture(gesture)
        
        # -------------------------
        # UI UPDATE
        # -------------------------
        self.window.update_head_angles(self.current_roll, self.current_pitch, self.current_yaw)
        self.window.update_landmarks(display)
        self.window.update_toggle(self.enabled)

        return True


    # -------------------------
    # UI HANDLERS
    # -------------------------
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

            # final step → persist
            self.config.set_calibration(
                self.min_pitch,
                self.max_pitch,
                self.min_yaw,
                self.max_yaw,
            )
            self.config.save_config()

    def on_mouse_speed_changed(self, speed):
        self.config.set_mouse_speed(speed)
        self.config.save_config()

    # -------------------------
    # LIFECYCLE
    # -------------------------
    def shutdown(self):
        if self.timer.isActive():
            self.timer.stop()

        if self.cap:
            self.cap.release()
            self.cap = None
        
        if self.active_key is not None:
            self.release_action(self.active_key)
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


    def _process_gesture(self, gesture):
        new_key = None

        # -------------------------
        # GESTURE PROCESSING
        # -------------------------
        if gesture:
            key = gesture["key"]
            self.window.update_gesture(gesture["name"])

            # -------------------------
            # TOGGLE (CONTROL ONLY)
            # -------------------------
            if key == "Toggle":
                now = time.time()

                if self.toggle_start_time is None:
                    self.toggle_start_time = now
                    self.toggle_triggered = False

                elif not self.toggle_triggered:
                    if now - self.toggle_start_time >= 1.0:
                        self.enabled = not self.enabled
                        self.toggle_triggered = True

                        # if disabling, release active input
                        if not self.enabled:
                            if self.active_key is not None:
                                self.release_action(self.active_key)
                                self.active_key = None

                new_key = None  # Toggle never enters input system

            # -------------------------
            # NORMAL GESTURES
            # -------------------------
            elif self.enabled and key != "Neutral":
                new_key = key

        else:
            self.window.update_gesture(None)

        # -------------------------
        # RESET TOGGLE IF NOT CONTINUOUS
        # -------------------------
        if not gesture or gesture["key"] != "Toggle":
            self.toggle_start_time = None
            self.toggle_triggered = False

        # -------------------------
        # INPUT STATE MACHINE
        # -------------------------
        if new_key != self.active_key:
            # release old
            if self.active_key is not None:
                self.release_action(self.active_key)

            # press new
            if new_key is not None:
                self.press_action(new_key)

            self.active_key = new_key