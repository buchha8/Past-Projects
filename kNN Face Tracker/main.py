import cv2
import landmarks
import ui


def main():
    cap = cv2.VideoCapture(0)
    landmarker = landmarks.create_landmarker()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        # ---- Pipeline ----
        face = landmarks.detect_face_landmarks(frame, landmarker, timestamp_ms)

        landmarks_pixels = landmarks.get_landmarks_pixels(face, frame)
        landmarks_centered = landmarks.get_landmarks_centered(landmarks_pixels)
        landmarks_normalized = landmarks.get_landmarks_normalized(
            landmarks_pixels, landmarks_centered
        )
        landmarks_display = landmarks.get_landmarks_display(landmarks_normalized)

        # ---- UI ----
        frame = ui.draw_landmarks_on_frame(frame, landmarks_pixels)
        norm_display = ui.draw_normalized_window(landmarks_display)
        ui.show(frame, norm_display)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()