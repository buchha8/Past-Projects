# Computer Vision Input Controller

Ergonomic Mouse + Keyboard control using Mediapipe facial recognition models.

Mouse movements controlled by head roll/pitch/yaw, keys and mouse clicks bound to facial gestures. Provides a UI to calibrate the facial software, record facial gestures, add new keybinds, and change other settings.

Facial recognition and landmarking are done through MediaPipe, which provides 478 points that are used for data processing, and 52 points for "blendshapes" (gesture estimates).

This was a personal project for my own use (chronic hand pain) and I can't guarantee continued updates or a bugfree experience, but feel free to use it if you'd like, and feel free to reach out to me!

![Example](https://github.com/buchha8/Past-Projects/blob/main/Computer%20Vision%20Input%20Controller/example.gif)

## How to use

Install Python and pip if not installed. Run "pip install requirements.txt". Then just run "python main.py" to run the program! Note that your webcam must be plugged in and not in-use by another program.

Click "Add Keybind" or "Delete Keybind" to add/remove gesture to input mappings. To map a gesture to an input, select the Keybind, click "Edit Gesture", name the gesture, strike your pose, and confirm once you are satisfied with the gesture. Select a gesture and click "Edit Sensitivity" to customize how easily/uneasily a gesture gets triggered.

"Neutral" and "Toggle" are two hardcoded "keybinds" that cannot be removed. Record a "Neutral" (resting) gesture for accurate gesture classification. Record a "Toggle" gesture for a convenient switch to enable/disable mouse and keyboard inputs.

Click "Calibrate" and record your head positions to scale mouse movements relative to your computer screen.

The "Mouse Speed" slider increases/decreases the speed that the mouse moves to new targets.

If you would like to disable gesture or mouse inputs manually, use the "Disable Gesture" and "Disable Mouse" toggles. This can be convenient if your use only requires one of the two (like if you want to use gestures for key presses but you don't want your face to move the mouse).

## Architecture

- `main.py`
  Starts the program and creates the orchestrator.

- `app_orchestrator.py`  
  Coordinates all modules. Has the main "frame loop" and functions to handle UI events and overarching control.

- `landmarks.py`  
  Extracts facial landmarks from the mediapipe model, calculates roll/pitch/yaw using rotation matrices, normalizes coordinates for animated face display in GUI.

- `gestures.py`  
  Gesture classification with cosine similarity, using the current frame's blendshape vector against all stored blendshape vectors. Also contains logic for how gestures should be processed and used.

- `input_controller.py`  
  Handles key presses and mouse clicks.

- `mouse_controller.py`  
  Controls mouse movements through:
  - Normalizing screen position using min/max pitch/yaw.
  - Kalman filter to reduce the noisiness of pitch/yaw, giving a stable estimate of where the user is looking on the screen.
  - PID controller (dx/dy output) which approaches the Kalman filtered position.
  - Deadzones for the mouse cursor with soft transition zones, preventing mouse jitter and making precise movements easier.

- `ui.py`
  Creation/display of UI elements, sends signals to orchestrator to process UI events.

- `config_manager.py`
  Contains config state data, as well as helper functions to read/write to the config file. "Source of truth".

- `config.json`
  Config file used to preserve state data between sessions. "Source of truth".

- `blaze_face_short_range.tflite`
  Used for face detection.

- `face_landmarker.task`
  Used by mediapipe to generate 478 facial landmarks, 52 blendshapes, and head rotation estimates.

- `requirements.txt`
  Required Python packages.

## AI Usage Disclosure

This project’s architecture, control systems, and design decisions were developed by me. AI tools were used to speed up implementation (e.g., scaffolding, refactoring, and debugging). All code was tested and validated manually.

## Disclaimer

This project is intended for personal productivity, accessibility, and experimentation.

Use of this software with third-party applications (including games) may violate their terms of service. The author is not responsible for any consequences resulting from such use.

## Third-Party Libraries

This project uses the following open source libraries:

* OpenCV
* MediaPipe
* PySide6 (Qt)
* NumPy
* PyAutoGUI
* pynput

Each library is subject to its own license.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

