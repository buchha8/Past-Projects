import sys
import config_manager
import ui
import app_orchestrator
import mouse_controller
import input_controller
import gestures
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer


def main():
    app = QApplication(sys.argv)
    # -------------------------
    # CORE STATE
    # -------------------------
    config = config_manager.ConfigManager()
    config.load_config()
    window = ui.MainWindow()
    mouse = mouse_controller.MouseController()
    gesture_processor = gestures.GestureProcessor()
    input = input_controller.InputController()
    orchestrator = app_orchestrator.AppOrchestrator(config, window, mouse, gesture_processor, input)

    # -------------------------
    # START
    # -------------------------
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()