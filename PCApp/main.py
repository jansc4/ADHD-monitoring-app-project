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
    
    # Inicjalizacja globalnego klienta API
    # TODO: Przenieś URL do pliku konfiguracyjnego
    api_client = APIClient(base_url="http://localhost:8000")
    
    # --- SplashScreen (opcjonalny) ---
    # splash = QSplashScreen(QPixmap("resources/splashscreen.png"))
    # splash.show()
    # app.processEvents()
    
    # Utworzenie głównego okna z przekazaniem api_client
    window = MainWindow(api_client)
    window.show()
    
    # splash.finish(window)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
