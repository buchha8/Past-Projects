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

def draw_normalized_landmarks(norm_lm, size=400):
    """
    Draw normalized landmarks on a square canvas.
    norm_lm: (68,2) normalized landmarks
    """
    canvas = np.zeros((size, size, 3), dtype=np.uint8)

    # Scale + center transform
    scale = size * 0.4   # controls zoom
    center = np.array([size // 2, size // 2])

    for (x, y) in norm_lm:
        px = int(center[0] + x * scale)
        py = int(center[1] + y * scale)
        cv2.circle(canvas, (px, py), 2, (0, 255, 0), -1)

    return canvas

def set_kalman_noise(kalman, q_exp, r_exp):
    q = 10 ** (-q_exp)
    r = 10 ** (-r_exp)

    for kf in kalman.kalman_filters:
        kf.processNoiseCov[:] = np.eye(4, dtype=np.float32) * q
        kf.measurementNoiseCov[:] = np.eye(2, dtype=np.float32) * r

# ---------------------------
# Main loop
# ---------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

kalman = LandmarkKalman(num_points=68)

# Create slider window
cv2.namedWindow("Kalman Controls")
cv2.createTrackbar("Q exp", "Kalman Controls", 4, 10, lambda x: None)
cv2.createTrackbar("R exp", "Kalman Controls", 1, 10, lambda x: None)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Read slider values
    q_exp = cv2.getTrackbarPos("Q exp", "Kalman Controls")
    r_exp = cv2.getTrackbarPos("R exp", "Kalman Controls")
    set_kalman_noise(kalman, q_exp, r_exp)

    # Face Detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3, 
        minNeighbors=5, 
        minSize=(60, 60)     # prevents tiny false positives
    )

    # Landmark Detection 
    lm_np = None
    if len(faces) > 0:
        ok, landmarks_list = facemark.fit(gray, faces)
        if ok:
            lm_np = landmarks_to_numpy(landmarks_list[0:1])  # first face only

    # Draw landmarks
    if lm_np is not None:
        for (x,y) in lm_np.astype(int):
            cv2.circle(frame, (x,y), 2, (0,0,255), -1)
    # Draw face rectangle
    if len(faces) > 0:
        x,y,w,h = faces[0]
        cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)

    cv2.imshow("Face Landmarks (Raw)", frame)

    # Draw normalized landmarks (Raw)
    if lm_np is not None:
        norm_lm = normalize_landmarks(lm_np)
        norm_canvas = draw_normalized_landmarks(norm_lm)
        cv2.imshow("Normalized Landmarks (Raw)", norm_canvas)

    # Draw normalized landmarks (Kalman)
    # Kalman smoothing
    smoothed_lm = kalman.update(lm_np)
    if smoothed_lm is not None:
        norm_lm = normalize_landmarks(smoothed_lm)
        norm_canvas = draw_normalized_landmarks(norm_lm)
        cv2.imshow("Normalized Landmarks (Kalman)", norm_canvas)

    # Show slider values
    cv2.putText(frame, f"Q=1e-{q_exp}", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.putText(frame, f"R=1e-{r_exp}", (10,60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()