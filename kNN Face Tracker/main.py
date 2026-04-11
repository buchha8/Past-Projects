import sys
import config_manager
import keybind_manager
import ui
import app_orchestrator
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer


def main():
    # -------------------------
    # CORE STATE
    # -------------------------
    config = config_manager.ConfigManager()
    config.load_config()
    keybinds = keybind_manager.KeybindManager(config)

    # -------------------------
    # QT APP
    # -------------------------
    app = QApplication(sys.argv)
    window = ui.MainWindow()
    orchestrator = app_orchestrator.AppOrchestrator(config, keybinds, window)

    # -------------------------
    # FRAME LOOP
    # -------------------------
    def tick():
        if not orchestrator.on_frame():
            timer.stop()
            app.quit()

    timer = QTimer()
    timer.timeout.connect(tick)
    timer.start(30)

    # -------------------------
    # SHUTDOWN HOOK
    # -------------------------
    def on_close():
        orchestrator.shutdown()

    window.on_close = on_close

    # -------------------------
    # START
    # -------------------------
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()