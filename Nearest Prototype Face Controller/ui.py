from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QHeaderView, QLineEdit,
    QPushButton, QSlider, QTableWidget, QTableWidgetItem, QDialog
)
from PySide6.QtGui import QImage, QPixmap, QKeySequence
import numpy as np


class MainWindow(QWidget):

    # -------------------------
    # SIGNALS (UI OUTPUT ONLY)
    # -------------------------
    add_keybind_requested = Signal(str)
    delete_keybind_requested = Signal(int)
    edit_gesture_requested = Signal(int, str)
    edit_sensitivity_requested = Signal(int, float)
    calibrate_requested = Signal(int)
    mouse_speed_changed = Signal(float)
    closed = Signal()
    disable_gestures_changed = Signal(bool)
    disable_mouse_changed = Signal(bool)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Face Control")

        layout = QVBoxLayout(self)

        # -------------------------
        # LANDMARKS
        # -------------------------
        self.landmarks_label = QLabel()
        self.landmarks_label.setFixedSize(200, 200)
        layout.addWidget(self.landmarks_label, alignment=Qt.AlignCenter)

        # -------------------------
        # CURRENT GESTURE
        # -------------------------
        self.gesture_label = QLabel("Current Gesture: --")
        layout.addWidget(self.gesture_label)
        self.toggle_label = QLabel("Toggle: --")
        layout.addWidget(self.toggle_label)

        # -------------------------
        # ANGLES
        # -------------------------
        angles = QHBoxLayout()

        self.roll_label = QLabel("Roll: --")
        self.pitch_label = QLabel("Pitch: --")
        self.yaw_label = QLabel("Yaw: --")

        angles.addWidget(self.roll_label)
        angles.addWidget(self.pitch_label)
        angles.addWidget(self.yaw_label)

        layout.addLayout(angles)

        # -------------------------
        # TABLE
        # -------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Key", "Gesture", "Sensitivity"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # -------------------------
        # BUTTONS
        # -------------------------
        btns = QHBoxLayout()

        self.add_btn = QPushButton("Add Keybind")
        self.del_btn = QPushButton("Delete Keybind")
        self.edit_gesture_btn = QPushButton("Edit Gesture")
        self.edit_sensitivity_btn = QPushButton("Edit Sensitivity")
        self.calibrate_btn = QPushButton("Calibrate")

        btns.addWidget(self.add_btn)
        btns.addWidget(self.del_btn)
        btns.addWidget(self.edit_gesture_btn)
        btns.addWidget(self.edit_sensitivity_btn)
        btns.addWidget(self.calibrate_btn)

        layout.addLayout(btns)

        # -------------------------
        # MOUSE SPEED
        # -------------------------
        self.mouse_speed_slider = QSlider(Qt.Horizontal)
        self.mouse_speed_slider.setMinimum(1)
        self.mouse_speed_slider.setMaximum(50)

        layout.addWidget(QLabel("Mouse Speed"))
        layout.addWidget(self.mouse_speed_slider)

        # -------------------------
        # DISABLE CONTROLS
        # -------------------------
        self.disable_gestures_checkbox = QPushButton("Disable Gestures")
        self.disable_gestures_checkbox.setCheckable(True)

        self.disable_mouse_checkbox = QPushButton("Disable Mouse")
        self.disable_mouse_checkbox.setCheckable(True)

        layout.addWidget(self.disable_gestures_checkbox)
        layout.addWidget(self.disable_mouse_checkbox)

        # -------------------------
        # SIGNAL WIRING (UI INTERNAL ONLY)
        # -------------------------
        self.add_btn.clicked.connect(self._on_add_clicked)
        self.del_btn.clicked.connect(self._on_delete_clicked)
        self.mouse_speed_slider.valueChanged.connect(self._on_mouse_speed_changed)
        self.edit_gesture_btn.clicked.connect(self._on_edit_gesture_clicked)
        self.edit_sensitivity_btn.clicked.connect(self._on_edit_sensitivity_clicked)
        self.calibrate_btn.clicked.connect(self._on_calibrate_clicked)
        self.disable_gestures_checkbox.toggled.connect(self.disable_gestures_changed.emit)
        self.disable_mouse_checkbox.toggled.connect(self.disable_mouse_changed.emit)
    
    # -------------------------
    # INTERNAL EVENT TRANSLATION
    # -------------------------
    def _on_add_clicked(self):
        dialog = InputCaptureDialog(self)

        if dialog.exec():
            value = dialog.value
            if value is not None:
                self.add_keybind_requested.emit(value)

    def _on_delete_clicked(self):
        row = self.table.currentRow()
        if row >= 0:
            self.delete_keybind_requested.emit(row)


    def _on_edit_gesture_clicked(self):
        row = self.table.currentRow()
        if row < 0:
            return

        dialog = GestureDialog(self)

        if dialog.exec():
            name = dialog.get_name()
            if name:
                self.edit_gesture_requested.emit(row, name)


    def _on_edit_sensitivity_clicked(self):
        row = self.table.currentRow()
        if row >= 0:
            current_value = float(self.table.item(row, 2).text())
            dialog = SensitivityDialog(current_value, self)
            if dialog.exec():
                new_value = dialog.get_value()
                self.edit_sensitivity_requested.emit(row, new_value)


    def _on_calibrate_clicked(self):
        steps = [
            "Look at the bottom edge of the monitor, then Confirm.",
            "Look at the top edge of the monitor, then Confirm.",
            "Look at the left edge of the monitor, then Confirm.",
            "Look at the right edge of the monitor, then Confirm.",
        ]

        for i, message in enumerate(steps):
            dialog = CalibrateDialog(message, self)

            # emit step index directly
            dialog.confirmed.connect(lambda i=i: self.calibrate_requested.emit(i))

            if not dialog.exec():
                return


    def _on_mouse_speed_changed(self, value):
        self.mouse_speed_changed.emit(value / 10.0)

    # -------------------------
    # RENDERING API (CALLED BY ORCHESTRATOR)
    # -------------------------
    def update_table(self, keybinds):
        self.table.setRowCount(0)
        for i, kb in enumerate(keybinds):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(kb["key"])))
            gesture = kb["gesture"]
            self.table.setItem(i, 1, QTableWidgetItem(gesture["name"] if gesture else "--"))
            self.table.setItem(i, 2, QTableWidgetItem(str(kb["sensitivity"])))


    def update_head_angles(self, roll, pitch, yaw):
        self.roll_label.setText(f"Roll: {roll:.1f}°" if roll else "Roll: --")
        self.pitch_label.setText(f"Pitch: {pitch:.1f}°" if pitch else "Pitch: --")
        self.yaw_label.setText(f"Yaw: {yaw:.1f}°" if yaw else "Yaw: --")


    def update_landmarks(self, landmarks_display):
        size = self.landmarks_label.width()
        img = np.zeros((size, size, 3), dtype=np.uint8)

        if landmarks_display is not None:
            for x, y in landmarks_display:
                xi = int(np.clip(x, 0, size - 1))
                yi = int(np.clip(y, 0, size - 1))
                img[yi, xi] = [0, 255, 0]

        qimg = QImage(img.data, size, size, 3 * size, QImage.Format_RGB888)
        self.landmarks_label.setPixmap(QPixmap.fromImage(qimg))


    def update_gesture(self, gesture):
        self.gesture_label.setText(f"Current Gesture: {gesture}" if gesture else "Current Gesture: --")
    
    def update_toggle(self, toggle_triggered):
        self.toggle_label.setText(f"Toggle: {'ON' if toggle_triggered else 'OFF'}")


    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)


class InputCaptureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = None
        self.setWindowTitle("Enter Input")
        layout = QVBoxLayout(self)

        self.label = QLabel("Press key or click")
        layout.addWidget(self.label)

    def keyPressEvent(self, event):
        key = event.key()
        key_str = QKeySequence(key).toString()
        if not key_str:
                key_str = str(key)  # fallback (rare)
        self.value = key_str
        self.accept()

    def mousePressEvent(self, event):
        button_map = {
            Qt.LeftButton: "Left Click",
            Qt.RightButton: "Right Click",
            Qt.MiddleButton: "Middle Click"
        }
        self.value = button_map.get(event.button(), "Mouse")
        self.accept()


class GestureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Gesture")

        self.name = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Enter a name, pose a gesture, then confirm when ready."))

        self.input = QLineEdit()
        self.input.setPlaceholderText("Gesture name")
        layout.addWidget(self.input)

        confirm = QPushButton("Confirm")
        confirm.clicked.connect(self.accept)

        layout.addWidget(confirm)

        # Allow Enter key to confirm
        self.input.returnPressed.connect(self.accept)

    def get_name(self):
        return self.input.text().strip()


class SensitivityDialog(QDialog):
    def __init__(self, initial_value, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Sensitivity")

        layout = QVBoxLayout(self)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(50)
        self.slider.setValue(int(initial_value * 10))

        self.label = QLabel(f"{initial_value:.1f}")

        confirm = QPushButton("Confirm")
        confirm.clicked.connect(self.accept)

        self.slider.valueChanged.connect(self._update_label)

        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        layout.addWidget(confirm)

    def _update_label(self, value):
        self.label.setText(f"{value / 10:.1f}")

    def get_value(self):
        return self.slider.value() / 10.0
    

class CalibrateDialog(QDialog):
    confirmed = Signal()

    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calibrate")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(message))

        confirm = QPushButton("Confirm")
        confirm.clicked.connect(self._on_confirm)

        layout.addWidget(confirm)

    def _on_confirm(self):
        self.confirmed.emit()
        self.accept()