import cv2
import numpy as np
import mediapipe as mp

# ---- Mediapipe Tasks Imports ----
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
Image = mp.Image

# ---- Webcam ----
cap = cv2.VideoCapture(0)

# ---- Load FaceLandmarker Model ----
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='face_landmarker.task'),
    running_mode=VisionRunningMode.VIDEO,
    output_face_blendshapes=True,
    output_facial_transformation_matrixes=True,
    num_faces=1
)
landmarker = FaceLandmarker.create_from_options(options)

# ---- Normalized landmark display settings ----
display_size = 400
half_size = display_size // 2

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

    timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
    results = landmarker.detect_for_video(mp_image, timestamp_ms)

    landmarks_pixels = None
    landmarks_normalized = None

    if results.face_landmarks:
        face = results.face_landmarks[0]

        # ---- Original pixel coordinates ----
        landmarks_pixels = np.array([[p.x * frame.shape[1],
                                      p.y * frame.shape[0],
                                      p.z * frame.shape[1]] for p in face], dtype=np.float32)

        # Draw landmarks on webcam feed
        for x, y, z in landmarks_pixels:
            cv2.circle(frame, (int(x), int(y)), 2, (0, 255, 0), -1)

        # ---- Face-centered normalization ----
        nose_idx = 1
        center = landmarks_pixels[nose_idx, :2]
        landmarks_centered = landmarks_pixels[:, :2] - center

        left_eye_idx, right_eye_idx = 33, 263
        eye_dist = np.linalg.norm(landmarks_pixels[left_eye_idx, :2] - landmarks_pixels[right_eye_idx, :2])
        landmarks_normalized = landmarks_centered / eye_dist

        # ---- Normalized display ----
        norm_display = np.zeros((display_size, display_size, 3), dtype=np.uint8)  # black background
        scale = half_size * 0.9
        landmarks_display = (landmarks_normalized * scale) + half_size

        # Draw landmarks as green dots
        for x, y in landmarks_display:
            cv2.circle(norm_display, (int(x), int(y)), 2, (0, 255, 0), -1)

        cv2.imshow("Normalized Landmarks", norm_display)

    cv2.imshow("FaceLandmarker", frame)

    if cv2.waitKey(1) == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()