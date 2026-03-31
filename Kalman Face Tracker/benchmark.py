# landmarks.py
import cv2
import numpy as np

# ---------------------------
# Load face detector and facemark
# ---------------------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Make sure you have opencv-contrib-python installed
facemark = cv2.face.createFacemarkLBF()
facemark.loadModel("lbfmodel.yaml")  # download from OpenCV GitHub: https://github.com/opencv/opencv_contrib/tree/master/modules/face

# ---------------------------
# Helper functions
# ---------------------------
def landmarks_to_numpy(landmarks):
    """
    Convert landmarks from facemark.fit output to shape (68,2)
    landmarks: list of shape (1,68,2) per face
    """
    lm_array = np.array(landmarks[0], dtype=np.float32)
    if lm_array.shape[0] != 68:
        lm_array = lm_array.reshape(-1, 2)
    return lm_array

def normalize_landmarks(landmarks):
    """Normalize landmarks relative to nose and inter-eye distance"""
    # Landmark indices (68-point model)
    NOSE = 30
    LEFT_EYE = 36
    RIGHT_EYE = 45

    nose = landmarks[NOSE]
    left_eye = landmarks[LEFT_EYE]
    right_eye = landmarks[RIGHT_EYE]

    scale = np.linalg.norm(left_eye - right_eye)
    normalized = (landmarks - nose) / scale
    return normalized

def extract_features(landmarks):
    """Extract simple feature vector: eyes horizontal ratio, vertical position, mouth openness/asymmetry"""
    lm = normalize_landmarks(landmarks)

    # Eye positions
    left_eye = lm[36:42]  # left eye 6 points
    right_eye = lm[42:48]  # right eye 6 points

    # Eye horizontal ratio
    left_eye_ratio = (left_eye[:,0].mean() - left_eye[0,0]) / (left_eye[3,0] - left_eye[0,0] + 1e-6)
    right_eye_ratio = (right_eye[:,0].mean() - right_eye[0,0]) / (right_eye[3,0] - right_eye[0,0] + 1e-6)

    # Eye vertical position
    left_eye_vertical = left_eye[:,1].mean()
    right_eye_vertical = right_eye[:,1].mean()

    # Mouth
    mouth = lm[48:68]
    mouth_left = mouth[0]
    mouth_right = mouth[6]
    mouth_top = mouth[3]
    mouth_bottom = mouth[9]

    mouth_asymmetry = mouth_left[1] - mouth_right[1]
    mouth_open = mouth_bottom[1] - mouth_top[1]

    features = np.array([
        left_eye_ratio,
        right_eye_ratio,
        left_eye_vertical,
        right_eye_vertical,
        mouth_asymmetry,
        mouth_open
    ])
    return features

# ---------------------------
# Main loop
# ---------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) > 0:
        # Detect landmarks for all faces
        ok, landmarks_list = facemark.fit(gray, faces)
        if ok:
            for rect, landmarks in zip(faces, landmarks_list):
                lm_np = landmarks_to_numpy(landmarks)
                features = extract_features(lm_np)
                print(np.round(features,3))

                # Draw landmarks
                for (x,y) in lm_np.astype(int):
                    cv2.circle(frame, (x,y), 2, (0,0,255), -1)

                # Draw face rectangle
                x, y, w, h = rect
                cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)

    cv2.imshow("Face Landmarks + Features", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()