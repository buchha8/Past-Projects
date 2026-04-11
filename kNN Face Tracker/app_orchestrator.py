import cv2
import landmarks
from PySide6.QtCore import QObject


class AppOrchestrator(QObject):
    """
    Central application controller:
    - Owns frame loop logic
    - Owns config + keybind mutations
    - Receives UI signals
    - Pushes render updates to UI
    """

    def __init__(self, config, keybinds, window):
        super().__init__()

        self.config = config
        self.keybinds = keybinds
        self.window = window

        # Camera / vision pipeline
        self.cap = cv2.VideoCapture(0)
        self.landmarker = landmarks.create_landmarker()

        # -------------------------
        # CONNECT UI SIGNALS
        # -------------------------
        self.window.add_keybind_requested.connect(self.on_add_keybind)
        self.window.delete_keybind_requested.connect(self.on_delete_keybind)
        self.window.edit_gesture_requested.connect(self.on_edit_gesture)
        self.window.calibrate_requested.connect(self.on_calibrate)
        self.window.mouse_speed_changed.connect(self.on_mouse_speed_changed)
        
        # -------------------------
        # INITIAL UI SYNC
        # -------------------------
        self.window.update_table(self.keybinds.get_keybinds())
        self.window.mouse_speed_slider.setValue(int(self.config.get_mouse_speed() * 10))


    # -------------------------
    # FRAME LOOP ENTRY POINT
    # -------------------------
    def on_frame(self):
        if not self.window.isVisible():
            self.shutdown()
            return False

        ret, frame = self.cap.read()
        if not ret:
            return True

        timestamp_ms = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
        results = landmarks.detect_face_data(frame, self.landmarker, timestamp_ms)

        # ---- pose + landmarks ----
        landmarks_pixels = landmarks.extract_landmarks_pixels(results, frame)
        transform_matrix = landmarks.extract_transform_matrix(results)

        roll, pitch, yaw = landmarks.compute_head_pose_angles(transform_matrix)

        centered = landmarks.compute_landmarks_centered(landmarks_pixels)
        normalized = landmarks.compute_landmarks_normalized(landmarks_pixels, centered)
        display = landmarks.compute_landmarks_display(normalized)

        # ---- UI updates ----
        self.window.update_head_angles(roll, pitch, yaw)
        self.window.update_landmarks(display)

        return True

    # -------------------------
    # UI EVENT HANDLERS
    # -------------------------
    def on_add_keybind(self, key):
        try:
            self.keybinds.add_keybind(key)
            self.config.save_config()
            self.window.update_table(self.keybinds.get_keybinds())
        except ValueError:
            pass

    def on_delete_keybind(self, index):
        self.keybinds.delete_keybind(index)
        self.config.save_config()
        self.window.update_table(self.keybinds.get_keybinds())


    def on_edit_gesture(self, index):
        # placeholder for GestureManager later
        print("Edit gesture:", index)


    def on_calibrate(self):
        # placeholder for CalibrationManager later
        print("Calibrate triggered")


    def on_mouse_speed_changed(self, speed):
        self.config.set_mouse_speed(speed)
        self.config.save_config()

    # -------------------------
    # KEYBIND ACCESS (UI READS ONLY THROUGH HERE IF NEEDED)
    # -------------------------
    def get_keybinds(self):
        return self.keybinds.get_keybinds()

    # -------------------------
    # LIFECYCLE
    # -------------------------
    def shutdown(self):
        if self.cap:
            self.cap.release()
            self.cap = None