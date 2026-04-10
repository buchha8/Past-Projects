# ui.py
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QTableWidget, QTableWidgetItem
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
import numpy as np


def create_ui(state_manager, keybind_manager):
    """
    Create the main UI window and return a tuple:
    (main_window, ui_state_dict)
    """

    ui_state = {}

    main_window = QWidget()
    main_window.setWindowTitle("Face Control")
    main_layout = QVBoxLayout(main_window)

    # ---- Landmarks display ----
    landmarks_label = QLabel()
    landmarks_label.setFixedSize(200, 200)
    main_layout.addWidget(landmarks_label, alignment=Qt.AlignHCenter)
    ui_state['landmarks_label'] = landmarks_label

    # ---- Roll/Pitch/Yaw labels ----
    angles_layout = QHBoxLayout()
    roll_label = QLabel("Roll: --")
    pitch_label = QLabel("Pitch: --")
    yaw_label = QLabel("Yaw: --")
    angles_layout.addWidget(roll_label)
    angles_layout.addWidget(pitch_label)
    angles_layout.addWidget(yaw_label)
    main_layout.addLayout(angles_layout)

    ui_state['roll_label'] = roll_label
    ui_state['pitch_label'] = pitch_label
    ui_state['yaw_label'] = yaw_label

    # ---- Keybind table ----
    keybind_table = QTableWidget()
    keybind_table.setColumnCount(3)
    keybind_table.setHorizontalHeaderLabels(["Key", "Gesture", "Sensitivity"])
    keybind_table.setEditTriggers(QTableWidget.NoEditTriggers)

    main_layout.addWidget(keybind_table)
    ui_state['keybind_table'] = keybind_table

    refresh_table(ui_state, state_manager)

    # ---- Buttons ----
    button_layout = QHBoxLayout()
    add_button = QPushButton("Add Keybind")
    delete_button = QPushButton("Delete Keybind")
    edit_button = QPushButton("Edit Gesture")
    calibrate_button = QPushButton("Calibrate")

    button_layout.addWidget(add_button)
    button_layout.addWidget(delete_button)
    button_layout.addWidget(edit_button)
    button_layout.addWidget(calibrate_button)

    main_layout.addLayout(button_layout)

    ui_state['add_button'] = add_button
    ui_state['delete_button'] = delete_button
    ui_state['edit_button'] = edit_button
    ui_state['calibrate_button'] = calibrate_button

    # FIXED: state passed explicitly
    add_button.clicked.connect(lambda: add_keybind(ui_state, keybind_manager, main_window))
    delete_button.clicked.connect(lambda: delete_keybind(ui_state, keybind_manager))

    # ---- Mouse speed slider ----
    mouse_speed_slider = QSlider()
    mouse_speed_slider.setOrientation(Qt.Horizontal)
    main_layout.addWidget(QLabel("Mouse Speed"))
    main_layout.addWidget(mouse_speed_slider)

    ui_state['mouse_speed_slider'] = mouse_speed_slider

    main_window.show()
    return main_window, ui_state


def update_head_angles(ui_state, roll, pitch, yaw):
    ui_state['roll_label'].setText(
        f"Roll: {roll:.1f}°" if roll is not None else "Roll: --"
    )
    ui_state['pitch_label'].setText(
        f"Pitch: {pitch:.1f}°" if pitch is not None else "Pitch: --"
    )
    ui_state['yaw_label'].setText(
        f"Yaw: {yaw:.1f}°" if yaw is not None else "Yaw: --"
    )


def update_landmarks_display(ui_state, landmarks_display):
    label = ui_state['landmarks_label']
    display_size = label.width()

    img = np.zeros((display_size, display_size, 3), dtype=np.uint8)

    if landmarks_display is not None:
        for x, y in landmarks_display:
            xi = int(np.clip(x, 0, display_size - 1))
            yi = int(np.clip(y, 0, display_size - 1))
            img[yi, xi] = [0, 255, 0]

    qimg = QImage(
        img.data,
        display_size,
        display_size,
        3 * display_size,
        QImage.Format_RGB888
    )

    label.setPixmap(QPixmap.fromImage(qimg))


def open_input_capture_dialog(parent=None):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Enter Input")

    layout = QVBoxLayout(dialog)
    label = QLabel("Enter Input")
    layout.addWidget(label)

    captured = {"value": None}

    def keyPressEvent(event):
        captured["value"] = event.text() or event.key()
        dialog.accept()

    def mousePressEvent(event):
        button_map = {
            Qt.LeftButton: "Mouse Left",
            Qt.RightButton: "Mouse Right",
            Qt.MiddleButton: "Mouse Middle"
        }
        captured["value"] = button_map.get(event.button(), "Mouse")
        dialog.accept()

    dialog.keyPressEvent = keyPressEvent
    dialog.mousePressEvent = mousePressEvent

    dialog.exec()
    return captured["value"]


# ----------------------------
# STATE-INTEGRATED FUNCTIONS
# ----------------------------

def add_keybind(ui_state, keybind_manager, main_window):
    key = open_input_capture_dialog(main_window)
    if key is None:
        return

    try:
        keybind_manager.add_keybind(key)
    except ValueError:
        return

    keybind_manager.state.save_state()
    refresh_table(ui_state, keybind_manager.state)


def delete_keybind(ui_state, keybind_manager):
    table = ui_state['keybind_table']

    row = table.currentRow()
    if row < 0:
        return

    keybind_manager.delete_keybind(row)

    keybind_manager.state.save_state()
    refresh_table(ui_state, keybind_manager.state)


def refresh_table(ui_state, state_manager):
    table = ui_state['keybind_table']
    keybinds = state_manager.get_state().get("keybinds", [])

    table.setRowCount(0)

    for row, kb in enumerate(keybinds):
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(str(kb["key"])))
        table.setItem(row, 1, QTableWidgetItem(str(kb["gesture"])))
        table.setItem(row, 2, QTableWidgetItem(str(kb["sensitivity"])))