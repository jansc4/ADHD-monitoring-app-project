"""Główne okno aplikacji - zoptymalizowana wersja."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget,
    QSystemTrayIcon, QMenu, QApplication
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

from customization_manager.settings_manager import SettingsManager
from customization_manager.strings_manager import StringsManager
from customization_manager.theme_manager import ThemeManager
from ui.components import TitleBar, WindowResizeHandler
from ui.settings_dialog import SettingsDialog
from ui.login_window import LoginPage
from pathlib import Path
import sys


class MainWindow(QMainWindow):
    """
    Główne okno aplikacji z:
    - Niestandardową belką tytułową
    - Przyciskiem ustawień w title bar
    - Floating settings dialog
    - Stroną logowania jako głównym widokiem
    - Obsługą tray icon
    - Zmianą rozmiaru okna bez ramki
    """
    
    def __init__(self, api_client):
        """
        Args:
            api_client: Globalny klient API do komunikacji z backendem
        """
        super().__init__()
        
        # Globalny api_client
        self.api_client = api_client
        
        # Konfiguracja okna
        self._setup_window()
        
        # Inicjalizacja menedżerów
        self._init_managers()
        
        # Inicjalizacja komponentów UI
        self._init_ui_components()
        
        # Aplikuj motyw
        self.rerender_theme()
        
    def _setup_window(self):
        """Konfiguruje podstawowe właściwości okna."""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMouseTracking(True)
        self.setGeometry(100, 100, 900, 700)
        
    def _init_managers(self):
        """Inicjalizuje menedżery konfiguracji."""
        self.settings = SettingsManager()
        self.strings = StringsManager(self.settings.get("language"))
        self.theme = ThemeManager(self.settings, self.strings)
        
        self.setWindowIcon(self.theme.colored_svg_icon(
            path=str("PCApp/resources/icons/image-svgrepo-com.svg"),
            color_key="highlight",
            size=256
        ))
    
    def _init_ui_components(self):
        """Inicjalizuje wszystkie komponenty UI."""
        # Handler zmiany rozmiaru okna
        self.resize_handler = WindowResizeHandler(self)
        
        # Tray icon
        self._setup_tray_icon()
        
        # Główny interfejs
        self._setup_ui()
        
        # Settings dialog (tworzony ale nie wyświetlany)
        self.settings_dialog = None
    
    def _setup_tray_icon(self):
        """Konfiguruje ikonę w system tray."""
        self.tray_icon = QSystemTrayIcon(self)
        self.icon = QIcon("PCApp/resources/icons/image-svgrepo-com.svg")  # tutaj placeholder ikony aplikacji
        self.tray_icon.setIcon(self.icon)
        self.tray_icon.setToolTip(self.strings.get("tooltip_app") or "Focusly")
        self.tray_icon.trans_tooltip_key = "tooltip_app"
        
        # Menu tray
        tray_menu = QMenu(self)

        restore_action = QAction(self.strings.get("action_restore") or "Restore", self)
        restore_action.trans_key = "action_restore"
        restore_action.triggered.connect(self.show_normal_from_tray)

        quit_action = QAction(self.strings.get("action_quit") or "Quit", self)
        quit_action.trans_key = "action_quit"
        quit_action.triggered.connect(self.close)
        
        tray_menu.addAction(restore_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def _setup_ui(self):
        """Tworzy główny interfejs użytkownika."""
        # Widget centralny
        central_widget = QWidget(objectName="centralWidget")
        central_widget.setMouseTracking(True)
        self.setCentralWidget(central_widget)
        
        # Belka tytułowa
        self.title_bar = TitleBar(self.theme, self.strings, self)
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.toggle_minimize)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize_restore)
        self.title_bar.fullscreen_clicked.connect(self.toggle_fullscreen)
        self.title_bar.settings_clicked.connect(self.show_settings)
        
        # Strona logowania jako główny widok
        self.login_page = LoginPage(self.strings, self.api_client, self)
        self.login_page.login_successful.connect(self._handle_login_success)
        
        # Layout główny
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.login_page)
        
        central_widget.setLayout(main_layout)
    
    def show_settings(self):
        """Wyświetla okno ustawień (floating)."""
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(
                self.settings,
                self.strings,
                self.theme,
                self
            )
            self.settings_dialog.settings_changed.connect(self.rerender_theme)
        
        # Pozycjonuj dialog względem głównego okna
        dialog_x = self.x() + (self.width() - self.settings_dialog.width()) // 2
        dialog_y = self.y() + (self.height() - self.settings_dialog.height()) // 2
        self.settings_dialog.move(dialog_x, dialog_y)
        
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
    
    def _handle_login_success(self, user_data: dict):
        """
        Obsługuje udane logowanie.
        
        Args:
            user_data: Dane zalogowanego użytkownika
        """
        print(f"Zalogowano użytkownika: {user_data}")
        # TODO: Przełącz na dashboard lub inny widok
        # TODO: Zapisz dane użytkownika w stanie aplikacji
    
    # === Metody sterowania oknem ===
    
    def toggle_maximize_restore(self):
        """Przełącza między maksymalizacją a normalnym rozmiarem."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def toggle_fullscreen(self):
        """Przełącza tryb pełnoekranowy."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def toggle_minimize(self):
        """Minimalizuje/przywraca okno."""
        if self.isMinimized():
            self.showNormal()
            self.activateWindow()
        else:
            self.showMinimized()
    
    def show_normal_from_tray(self):
        """Przywraca okno z tray."""
        self.showNormal()
        self.raise_()
        self.activateWindow()
    
    # === Obsługa zdarzeń myszy ===
    
    def mousePressEvent(self, event):
        """Deleguje obsługę do resize handler."""
        self.resize_handler.mouse_press(event)
    
    def mouseMoveEvent(self, event):
        """Deleguje obsługę do resize handler."""
        self.resize_handler.mouse_move(event)
    
    def mouseReleaseEvent(self, event):
        """Deleguje obsługę do resize handler."""
        self.resize_handler.mouse_release(event)
    
    def keyPressEvent(self, event):
        """Obsługa skrótów klawiszowych."""
        if event.key() == Qt.Key.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
    
    # === Odświeżanie motywu/języka ===
    
    def rerender_theme(self):
        """Odświeża motyw i język we wszystkich komponentach."""
        # Aktualizuj menedżery
        self.strings = StringsManager(self.settings.get("language"))
        self.theme.apply_theme(QApplication.instance())
        
        # Odśwież wszystkie dzieci
        for child in self.findChildren(QWidget):
            self._rerender_children(child)
        
        # Odśwież dialog ustawień jeśli istnieje
        if self.settings_dialog is not None:
            self.settings_dialog.rerender_theme()
    
    def _rerender_children(self, widget):
        """
        Rekurencyjnie odświeża widget i jego dzieci.
        
        Args:
            widget: Widget do odświeżenia
        """
        # 1. Wywołaj metodę rerender_theme jeśli istnieje
        if hasattr(widget, "rerender_theme"):
            widget.rerender_theme()
        
        # 2. Zaktualizuj tekst jeśli ma trans_key
        if hasattr(widget, "trans_key") and hasattr(widget, "setText"):
            try:
                new_text = self.strings.get(widget.trans_key)
                widget.setText(new_text)
            except Exception as e:
                print(f"[WARN] Nie udało się ustawić tekstu dla: {widget} ({widget.trans_key}): {e}")
        
        # 3. Zaktualizuj placeholder jeśli ma trans_placeholder_key
        if hasattr(widget, "trans_placeholder_key") and hasattr(widget, "setPlaceholderText"):
            try:
                new_text = self.strings.get(widget.trans_placeholder_key)
                widget.setPlaceholderText(new_text)
            except Exception as e:
                print(f"[WARN] Nie udało się ustawić placeholder dla: {widget}: {e}")
        
        # 4. Zaktualizuj tooltip jeśli ma trans_tooltip_key
        if hasattr(widget, "trans_tooltip_key"):
            widget.setToolTip(self.strings.get(widget.trans_tooltip_key))
        
        # 5. Zaktualizuj QAction jeśli ma trans_key
        if isinstance(widget, QAction) and hasattr(widget, "trans_key"):
            widget.setText(self.strings.get(widget.trans_key))
        
        # 6. Rekurencja dla dzieci
        for child in widget.findChildren(QWidget):
            self._rerender_children(child)
