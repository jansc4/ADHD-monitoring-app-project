"""Główne okno aplikacji."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QSystemTrayIcon, QMenu, QApplication, QStackedWidget
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

# ================= IMPORTY PROJEKTOWE =================

from PCApp.customization_manager.settings_manager import SettingsManager
from PCApp.customization_manager.strings_manager import StringsManager
from PCApp.customization_manager.theme_manager import ThemeManager

from PCApp.ui.components import TitleBar, WindowResizeHandler
from PCApp.ui.settings_dialog import SettingsDialog
from PCApp.ui.login_window import LoginPage
from PCApp.ui.patient_dashboard import PatientDashboard
from PCApp.ui.doctor_dashboard import DoctorDashboard

from PCApp.api_client import APIClient


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self._setup_window()
        self._init_managers()
        self._init_ui_components()
        self.rerender_theme()
        self._apply_focusly_style()

    # ================= OKNO =================

    def _setup_window(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMouseTracking(True)
        self.setGeometry(100, 100, 900, 700)

    # ================= MANAGERY =================

    def _init_managers(self):
        self.settings = SettingsManager()
        self.strings = StringsManager(self.settings.get("language"))
        self.theme = ThemeManager(self.settings, self.strings)

        self.api_client = APIClient(
            self.settings.get("api_url") or "http://127.0.0.1:8000"
        )

    # ================= UI =================

    def _init_ui_components(self):
        self.resize_handler = WindowResizeHandler(self)
        self._setup_tray_icon()

        central_widget = QWidget(objectName="centralWidget")
        self.setCentralWidget(central_widget)

        # TITLE BAR
        self.title_bar = TitleBar(self.theme, self.strings, self)
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.toggle_minimize)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize_restore)
        self.title_bar.fullscreen_clicked.connect(self.toggle_fullscreen)
        self.title_bar.settings_clicked.connect(self.show_settings)

        # STACKED WIDGET (widoki)
        self.stacked_widget = QStackedWidget()

        # LOGIN
        self.login_page = LoginPage(self.strings, self.api_client, self)
        self.login_page.login_successful.connect(self._handle_login_success)
        self.stacked_widget.addWidget(self.login_page)

        # DASHBOARD (dynamiczny)
        self.dashboard = None

        # LAYOUT
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.title_bar)
        layout.addWidget(self.stacked_widget)

        central_widget.setLayout(layout)

        self.settings_dialog = None

    # ================= TRAY ICON =================

    def _setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)

        icon_path = self.settings.get("placeholder_image_path")
        if icon_path:
            self.tray_icon.setIcon(QIcon(icon_path))

        self.tray_icon.setToolTip("Focusly")

        tray_menu = QMenu(self)

        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self.show_normal_from_tray)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)

        tray_menu.addAction(restore_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    # ================= LOGOWANIE =================

    def _handle_login_success(self, user_data: dict):
        print("✅ Zalogowano:", user_data)

        role = user_data.get("role")
        print("➡️ ROLA UŻYTKOWNIKA:", role)

        # usuń stary dashboard (jeśli istniał)
        if self.dashboard is not None:
            self.stacked_widget.removeWidget(self.dashboard)
            self.dashboard.deleteLater()
            self.dashboard = None

        # routing po roli
        if role == "doctor":
            self.dashboard = DoctorDashboard(user_data)
        else:
            self.dashboard = PatientDashboard(user_data)

        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.setCurrentWidget(self.dashboard)

    # ================= USTAWIENIA =================

    def show_settings(self):
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(
                self.settings,
                self.strings,
                self.theme,
                self
            )
            self.settings_dialog.settings_changed.connect(self.rerender_theme)

        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    # ================= OKNO – STEROWANIE =================

    def toggle_maximize_restore(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def toggle_minimize(self):
        self.showMinimized()

    def show_normal_from_tray(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def mousePressEvent(self, event):
        self.resize_handler.mouse_press(event)

    def mouseMoveEvent(self, event):
        self.resize_handler.mouse_move(event)

    def mouseReleaseEvent(self, event):
        self.resize_handler.mouse_release(event)

    # ================= THEME =================

    def rerender_theme(self):
        self.theme.apply_theme(QApplication.instance())

    # ================= DESIGN =================

    def _apply_focusly_style(self):
        self.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(
                x1:0, y1:0,
                x2:1, y2:1,
                stop:0 #020024,
                stop:0.4 #090979,
                stop:1 #3f32ff
            );
            border-radius: 16px;
        }

        QWidget#centralWidget {
            background: transparent;
        }

        QLabel {
            background: transparent;
            color: white;
            font-size: 14px;
        }
        """)
