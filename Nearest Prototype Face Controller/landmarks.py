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
def detect_face_data(frame, landmarker, timestamp_ms):
    """
    Returns raw Mediapipe results object only.
    """
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    results = landmarker.detect_for_video(mp_image, timestamp_ms)
    return results


def extract_landmarks_pixels(results, frame):
    if not results.face_landmarks:
        return None
    face = results.face_landmarks[0]
    return np.array([[p.x * frame.shape[1], p.y * frame.shape[0], p.z * frame.shape[1]] for p in face], dtype=np.float32)


def extract_transform_matrix(results):
    if not results.facial_transformation_matrixes:
        return None
    return np.array(results.facial_transformation_matrixes[0]).reshape(4,4)


def extract_blendshape_vector(results):
    if not results.face_blendshapes:
        return None
    blendshapes = results.face_blendshapes[0]
    return {
        bs.category_name: float(bs.score)
        for bs in blendshapes
    }


def compute_head_pose_angles(transform_matrix):
    if transform_matrix is None:
        return None, None, None

    R = transform_matrix[:3,:3]

    yaw = -2*np.arctan2(-R[2,0], np.sqrt(R[2,1]**2 + R[2,2]**2))  # turn
    roll   = np.arctan2(R[1,0], R[0,0])                            # tilt
    pitch  = -2*np.arctan2(R[2,1], R[2,2])                            # nod

    return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)


def compute_landmarks_centered(landmarks_pixels):
    if landmarks_pixels is None:
        return None

    nose_idx = 1
    center = landmarks_pixels[nose_idx, :2]
    return landmarks_pixels[:, :2] - center


def compute_landmarks_normalized(landmarks_pixels, landmarks_centered):
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


def compute_landmarks_display(landmarks_normalized, display_size=200):
    if landmarks_normalized is None:
        return None

    half_size = display_size // 2
    scale = half_size * 0.9

    # scale and shift
    landmarks_display = (landmarks_normalized * scale) + half_size

    # flip left/right by inverting X coordinates
    landmarks_display[:, 0] = display_size - landmarks_display[:, 0]

    return landmarks_display


def process_landmarks_pipeline(results, frame):
    """
    Full landmarks pipeline:
    - extract pixels
    - extract transform
    - compute head pose
    - compute display coordinates

    Returns:
        display, roll, pitch, yaw
    """

    landmarks_pixels = extract_landmarks_pixels(results, frame)
    transform_matrix = extract_transform_matrix(results)

    roll, pitch, yaw = compute_head_pose_angles(transform_matrix)

    centered = compute_landmarks_centered(landmarks_pixels)
    normalized = compute_landmarks_normalized(landmarks_pixels, centered)
    display = compute_landmarks_display(normalized)

    return display, roll, pitch, yaw