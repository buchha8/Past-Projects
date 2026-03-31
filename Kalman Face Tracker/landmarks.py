# landmarks_kalman.py
import cv2
import numpy as np

# ---------------------------
# Load face detector and facemark
# ---------------------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
facemark = cv2.face.createFacemarkLBF()
facemark.loadModel("lbfmodel.yaml")  # download from OpenCV contrib GitHub

# ---------------------------
# Kalman filter per landmark
# ---------------------------
class LandmarkKalman:
    def __init__(self, num_points):
        # State: [x, y, vx, vy] per point
        self.num_points = num_points
        self.kalman_filters = []
        for _ in range(num_points):
            kf = cv2.KalmanFilter(4, 2)  # 4 state (x,y,vx,vy), 2 measurements (x,y)
            kf.transitionMatrix = np.array([[1,0,1,0],
                                            [0,1,0,1],
                                            [0,0,1,0],
                                            [0,0,0,1]], dtype=np.float32)
            kf.measurementMatrix = np.eye(2,4, dtype=np.float32)
            kf.processNoiseCov = np.eye(4, dtype=np.float32) * 1e-3
            kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 1e-2
            kf.errorCovPost = np.eye(4, dtype=np.float32)
            self.kalman_filters.append(kf)
        self.initialized = False

    def update(self, points):
        """points: (num_points,2) or None"""
        smoothed = np.zeros((self.num_points,2), dtype=np.float32)
        for i, kf in enumerate(self.kalman_filters):
            if points is not None:
                measurement = np.array([[points[i,0]], [points[i,1]]], dtype=np.float32)
                if not self.initialized:
                    kf.statePost[:2] = measurement
                    kf.statePost[2:] = 0
                kf.correct(measurement)
                # prediction
                pred = kf.predict()
                smoothed[i] = pred[:2].ravel()
            else:
                # no measurement → just keep previous state
                smoothed[i] = kf.statePost[:2].ravel()
        self.initialized = True
        return smoothed

# ---------------------------
# Helper functions
# ---------------------------
def landmarks_to_numpy(landmarks):
    """Convert facemark output to shape (68,2)"""
    lm_array = np.array(landmarks[0], dtype=np.float32)
    if lm_array.shape[0] != 68:
        lm_array = lm_array.reshape(-1,2)
    return lm_array

def normalize_landmarks(landmarks):
    """Normalize relative to nose and inter-eye distance"""
    NOSE = 30
    LEFT_EYE = 36
    RIGHT_EYE = 45
    nose = landmarks[NOSE]
    left_eye = landmarks[LEFT_EYE]
    right_eye = landmarks[RIGHT_EYE]
    scale = np.linalg.norm(left_eye - right_eye)
    normalized = (landmarks - nose) / (scale + 1e-6)
    return normalized

# ---------------------------
# Main loop
# ---------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

kalman = LandmarkKalman(num_points=68)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    lm_np = None
    if len(faces) > 0:
        ok, landmarks_list = facemark.fit(gray, faces)
        if ok:
            lm_np = landmarks_to_numpy(landmarks_list[0:1])  # first face only

    # Kalman smoothing
    smoothed_lm = kalman.update(lm_np)

    # Draw landmarks
    for (x,y) in smoothed_lm.astype(int):
        cv2.circle(frame, (x,y), 2, (0,0,255), -1)
    # Draw face rectangle
    if len(faces) > 0:
        x,y,w,h = faces[0]
        cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)

    cv2.imshow("Face Landmarks + Kalman", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()