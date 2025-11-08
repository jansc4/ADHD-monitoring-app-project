"""Punkt wejścia aplikacji Focusly."""

import sys
import ctypes
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap

from ui.main_window import MainWindow
from api_client import APIClient

# Ustawienie unikalnego ID aplikacji dla systemu Windows
APP_ID = 'EternalLab.Apps.Focusly.v0.1'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)


def main():
    """Główna funkcja aplikacji."""
    app = QApplication(sys.argv)
    

    
    # --- SplashScreen (opcjonalny) ---
    # splash = QSplashScreen(QPixmap("resources/splashscreen.png"))
    # splash.show()
    # app.processEvents()
    
    # Utworzenie głównego okna z przekazaniem api_client
    window = MainWindow()
    window.show()
    
    # splash.finish(window)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
