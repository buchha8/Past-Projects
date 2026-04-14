import sys
import config_manager
import ui
import app_orchestrator
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
    orchestrator = app_orchestrator.AppOrchestrator(config, window)
    
    # -------------------------
    # START
    # -------------------------
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()