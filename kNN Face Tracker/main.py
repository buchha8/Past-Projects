import sys
import cv2
import landmarks
import config_manager
import keybind_manager
import ui
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

def main():
    as_manager = config_manager.ConfigManager()
    as_manager.load_config()  # Load saved keybinds and settings

    kb_manager = keybind_manager.KeybindManager(as_manager)
    
    # ---- Qt application ----
    app = QApplication(sys.argv)
    main_window, ui_state = ui.create_ui(as_manager, kb_manager)  # create UI and return state dict

    # ---- OpenCV capture and landmarker ----
    cap = cv2.VideoCapture(0)
    landmarker = landmarks.create_landmarker()

    # ---- Frame update function ----
    def update_frame():
        if not main_window.isVisible():  # stop when window closed
            cap.release()
            app.quit()
            return

        ret, frame = cap.read()
        if not ret:
            return

        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        results = landmarks.detect_face_data(frame, landmarker, timestamp_ms)

        # ---- Landmarks and pose ----
        landmarks_pixels = landmarks.extract_landmarks_pixels(results, frame)
        transform_matrix = landmarks.extract_transform_matrix(results)
        roll, pitch, yaw = landmarks.compute_head_pose_angles(transform_matrix)
        landmarks_centered = landmarks.compute_landmarks_centered(landmarks_pixels)
        landmarks_normalized = landmarks.compute_landmarks_normalized(landmarks_pixels, landmarks_centered)
        landmarks_display = landmarks.compute_landmarks_display(landmarks_normalized)

        # ---- Blendshapes (for gestures) ----
        blendshape_vector = landmarks.extract_blendshape_vector(results)
        # print("Face Blendshapes:", results.face_blendshapes)  # Debug print, can be removed later
        # print("Blendshapes:", blendshape_vector)  # Debug print, can be removed later

        # ---- Update UI ----
        ui.update_landmarks_display(ui_state, landmarks_display)
        ui.update_head_angles(ui_state, roll, pitch, yaw)
        # ui.update_blendshapes(ui_state, blendshape_vector)

        # Future: handle mouse actions / keybinds here

    # ---- QTimer for event-driven updates ----
    timer = QTimer()
    timer.timeout.connect(update_frame)
    timer.start(30)  # ~33 FPS

    # ---- Start Qt event loop ----
    sys.exit(app.exec())

if __name__ == "__main__":
    main()