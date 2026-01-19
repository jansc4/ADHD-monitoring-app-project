"""Punkt wejścia aplikacji Focusly."""

import sys
import ctypes
import platform

from PyQt6.QtWidgets import QApplication

# ✅ POPRAWNE IMPORTY PAKIETOWE
from PCApp.ui.main_window import MainWindow
from PCApp.api_client import APIClient


def set_windows_app_id(app_id: str) -> None:
    
    if platform.system() == "Windows":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass


def main():
    APP_ID = "EternalLab.Apps.Focusly.v0.1"
    set_windows_app_id(APP_ID)

    app = QApplication(sys.argv)

    # API Client
    api_client = APIClient("http://127.0.0.1:8000")

    # Main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
