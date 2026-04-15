import sys
import config_manager
import ui
import app_orchestrator
import mouse_controller
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
    orchestrator = app_orchestrator.AppOrchestrator(config, window, mouse)
    
    # -------------------------
    # START
    # -------------------------
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()