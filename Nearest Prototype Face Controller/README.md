# Work in Progress!

Ergonomic Mouse + Keyboard control using facial recognition.

Mouse movements controlled by head roll/pitch/yaw, keys and mouse clicks bound to facial gestures. Provides a UI to calibrate the facial software, record facial gestures, add new keybinds, and change other settings.

Facial recognition and landmarking are done through MediaPipe, which provides 478 points that are used for data processing. Rotation Matrices are used to calculate Roll/Pitch/Yaw, which control mouse movements, scaling linearly. Template matching and k-nearest neighbors are used to classify facial gestures.

![Work in Progress](https://github.com/buchha8/Past-Projects/blob/main/kNN%20Face%20Tracker/example.png)