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
        results = landmarks.detect_face_data(frame, landmarker, timestamp_ms)
        landmarks_pixels = landmarks.get_landmarks_pixels(results, frame)
        transform_matrix = landmarks.get_transform_matrix(results)
        blendshape_vector = landmarks.get_blendshape_vector(results)
        roll, pitch, yaw = landmarks.get_head_pose_angles(transform_matrix)
        landmarks_centered = landmarks.get_landmarks_centered(landmarks_pixels)
        landmarks_normalized = landmarks.get_landmarks_normalized(landmarks_pixels, landmarks_centered)
        landmarks_display = landmarks.get_landmarks_display(landmarks_normalized)
        # if transform_matrix is not None:
            # print(f"Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")
        # if blendshape_vector is not None:
            # print(f"Blendshapes: {blendshape_vector}")

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