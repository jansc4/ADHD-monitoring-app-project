"""Główne okno aplikacji."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QSystemTrayIcon, QMenu, QApplication, QStackedWidget
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

# ================= IMPORTY =================

from PCApp.customization_manager.settings_manager import SettingsManager
from PCApp.customization_manager.strings_manager import StringsManager
from PCApp.customization_manager.theme_manager import ThemeManager

from PCApp.ui.components import TitleBar, WindowResizeHandler
from PCApp.ui.settings_dialog import SettingsDialog
from PCApp.ui.login_window import LoginPage

from PCApp.ui.game_widget import GameView
from PCApp.ui.patient_dashboard import PatientDashboard
from PCApp.ui.doctor_dashboard import DoctorDashboard
from PCApp.ui.doctor_profile_view import DoctorProfileView
from PCApp.ui.sidebar import Sidebar

from PCApp.api_client import APIClient


class MainWindow(QMainWindow):

    # ================= INIT =================

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
        self.setGeometry(100, 100, 1000, 700)

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

        # CONTENT
        self.sidebar = None
        self.stacked_widget = QStackedWidget()

        self.login_page = LoginPage(self.strings, self.api_client, self)
        self.login_page.login_successful.connect(self._handle_login_success)
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.setCurrentWidget(self.login_page)

        self.game_view = GameView()
        self.game_view.finished.connect(self.on_game_finished)
        self.stacked_widget.addWidget(self.game_view)

        self.doctor_dashboard = None
        self.doctor_profile_view = None
        self.patient_dashboard = None

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.stacked_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.title_bar)
        main_layout.addLayout(content_layout)

        central_widget.setLayout(main_layout)

        self.content_layout = content_layout
        self.settings_dialog = None

    # ================= LOGOWANIE =================

    def _handle_login_success(self, user_data: dict):
        role = user_data.get("role")

        for widget in (
            self.sidebar,
            self.doctor_dashboard,
            self.doctor_profile_view,
            self.patient_dashboard
        ):
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        self.sidebar = None
        self.doctor_dashboard = None
        self.doctor_profile_view = None
        self.patient_dashboard = None

        if role == "doctor":
            self.sidebar = Sidebar(self)
            self.content_layout.insertWidget(0, self.sidebar)

            self.doctor_dashboard = DoctorDashboard(user_data, self)
            self.doctor_profile_view = DoctorProfileView(user_data, self)

            self.stacked_widget.addWidget(self.doctor_dashboard)
            self.stacked_widget.addWidget(self.doctor_profile_view)
            self.stacked_widget.setCurrentWidget(self.doctor_dashboard)
        else:
            self.patient_dashboard = PatientDashboard(user_data, self)
            self.stacked_widget.addWidget(self.patient_dashboard)
            self.stacked_widget.setCurrentWidget(self.patient_dashboard)

    # ================= SIDEBAR =================

    def show_doctor_dashboard(self):
        self.stacked_widget.setCurrentWidget(self.doctor_dashboard)

    def show_doctor_profile(self):
        self.stacked_widget.setCurrentWidget(self.doctor_profile_view)

    def logout(self):
        if self.sidebar:
            self.sidebar.setParent(None)
            self.sidebar.deleteLater()
            self.sidebar = None

        self.stacked_widget.setCurrentWidget(self.login_page)

    # ================= GRA =================

    def start_game(self):
        self.game_view.start_game()
        self.stacked_widget.setCurrentWidget(self.game_view)

    def on_game_finished(self, result):
        print("Wynik gry:", result)
        if self.patient_dashboard:
            self.stacked_widget.setCurrentWidget(self.patient_dashboard)
        else:
            self.stacked_widget.setCurrentWidget(self.login_page)

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

    # ================= TRAY =================

    def _setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)

        tray_menu = QMenu(self)
        tray_menu.addAction(QAction("Restore", self, triggered=self.show_normal_from_tray))
        tray_menu.addAction(QAction("Quit", self, triggered=QApplication.quit))

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    # ================= OKNO =================

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
        }

        QWidget#centralWidget {
            background: transparent;
        }
        """)
