import cv2
import gestures
import landmarks
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

        roll, pitch, yaw = landmarks.compute_head_pose_angles(transform_matrix)

        centered = landmarks.compute_landmarks_centered(landmarks_pixels)
        normalized = landmarks.compute_landmarks_normalized(landmarks_pixels, centered)
        display = landmarks.compute_landmarks_display(normalized)

        self.window.update_head_angles(roll, pitch, yaw)
        self.window.update_landmarks(display)
        self.window.update_gesture(None)

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

    def on_calibrate(self):
        print("Calibrate triggered")

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