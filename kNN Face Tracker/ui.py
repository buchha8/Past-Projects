import cv2
import numpy as np


def draw_landmarks_on_frame(frame, landmarks_pixels):
    if landmarks_pixels is None:
        return frame

    for x, y, _ in landmarks_pixels:
        cv2.circle(frame, (int(x), int(y)), 2, (0, 255, 0), -1)

    return frame


def draw_normalized_window(landmarks_display, display_size=400):
    if landmarks_display is None:
        return None

    canvas = np.zeros((display_size, display_size, 3), dtype=np.uint8)

    for x, y in landmarks_display:
        cv2.circle(canvas, (int(x), int(y)), 2, (0, 255, 0), -1)

    return canvas


def show(frame, norm_display):
    cv2.imshow("FaceLandmarker", frame)

    if norm_display is not None:
        cv2.imshow("Normalized Landmarks", norm_display)