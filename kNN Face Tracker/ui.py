from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
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
    edit_gesture_requested = Signal(int)
    calibrate_requested = Signal()
    mouse_speed_changed = Signal(float)
    closed = Signal()

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

        layout.addWidget(self.table)

        # -------------------------
        # BUTTONS
        # -------------------------
        btns = QHBoxLayout()

        self.add_btn = QPushButton("Add Keybind")
        self.del_btn = QPushButton("Delete Keybind")
        self.edit_btn = QPushButton("Edit Gesture")
        self.calibrate_btn = QPushButton("Calibrate")

        btns.addWidget(self.add_btn)
        btns.addWidget(self.del_btn)
        btns.addWidget(self.edit_btn)
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
        # SIGNAL WIRING (UI INTERNAL ONLY)
        # -------------------------
        self.add_btn.clicked.connect(self._on_add_clicked)
        self.del_btn.clicked.connect(self._on_delete_clicked)
        self.mouse_speed_slider.valueChanged.connect(self._on_mouse_speed_changed)
        self.edit_btn.clicked.connect(self._on_edit_gesture_clicked)
        self.calibrate_btn.clicked.connect(self._on_calibrate_clicked)
    
    # -------------------------
    # INTERNAL EVENT TRANSLATION
    # -------------------------
    def _on_add_clicked(self):
        key = self._capture_input()
        if key:
            self.add_keybind_requested.emit(str(key))

    def _on_delete_clicked(self):
        row = self.table.currentRow()
        if row >= 0:
            self.delete_keybind_requested.emit(row)


    def _on_edit_gesture_clicked(self):
        row = self.table.currentRow()
        if row >= 0:
            self.edit_gesture_requested.emit(row)

    def _on_calibrate_clicked(self):
        self.calibrate_requested.emit()


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
            self.table.setItem(i, 1, QTableWidgetItem(str(kb["gesture"])))
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

    # -------------------------
    # INPUT DIALOG
    # -------------------------
    def _capture_input(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Enter Input")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Press key or click mouse"))

        captured = {"value": None}


        def keyPressEvent(event):
            key = event.key()

            key_str = QKeySequence(key).toString()

            if not key_str:
                key_str = str(key)  # fallback (rare)

            captured["value"] = key_str
            dialog.accept()

        def mousePressEvent(event):
            button_map = {
                Qt.LeftButton: "Left Click",
                Qt.RightButton: "Right Click",
                Qt.MiddleButton: "Middle Click"
            }
            captured["value"] = button_map.get(event.button(), "Mouse")
            dialog.accept()

        dialog.keyPressEvent = keyPressEvent
        dialog.mousePressEvent = mousePressEvent

        dialog.exec()
        return captured["value"]
    

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)