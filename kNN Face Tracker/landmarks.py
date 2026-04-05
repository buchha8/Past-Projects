import cv2
import numpy as np
import mediapipe as mp

# ---- Mediapipe Tasks Imports ----
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
Image = mp.Image


# ---- Initialization ----
def create_landmarker(model_path="face_landmarker.task"):
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1
    )
    return FaceLandmarker.create_from_options(options)


# ---- Core processing ----
def detect_face_landmarks(frame, landmarker, timestamp_ms):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

    results = landmarker.detect_for_video(mp_image, timestamp_ms)

    if not results.face_landmarks:
        return None

    return results.face_landmarks[0]


def get_landmarks_pixels(face_landmarks, frame):
    if face_landmarks is None:
        return None

    return np.array([
        [p.x * frame.shape[1], p.y * frame.shape[0], p.z * frame.shape[1]]
        for p in face_landmarks
    ], dtype=np.float32)


def get_landmarks_centered(landmarks_pixels):
    if landmarks_pixels is None:
        return None

    nose_idx = 1
    center = landmarks_pixels[nose_idx, :2]
    return landmarks_pixels[:, :2] - center


def get_landmarks_normalized(landmarks_pixels, landmarks_centered):
    if landmarks_pixels is None or landmarks_centered is None:
        return None

    left_eye_idx, right_eye_idx = 33, 263
    eye_dist = np.linalg.norm(
        landmarks_pixels[left_eye_idx, :2] -
        landmarks_pixels[right_eye_idx, :2]
    )

    if eye_dist == 0:
        return None

    return landmarks_centered / eye_dist


def get_landmarks_display(landmarks_normalized, display_size=400):
    if landmarks_normalized is None:
        return None

    half_size = display_size // 2
    scale = half_size * 0.9

    return (landmarks_normalized * scale) + half_size