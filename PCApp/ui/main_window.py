"""
Główne okno aplikacji.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QSystemTrayIcon, QMenu,
    QApplication, QStackedWidget
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from PCApp.customization_manager.settings_manager import SettingsManager
from PCApp.customization_manager.strings_manager import StringsManager
from PCApp.customization_manager.theme_manager import ThemeManager

from PCApp.ui.components import TitleBar, WindowResizeHandler
from PCApp.ui.settings_dialog import SettingsDialog
from PCApp.ui.login_window import LoginPage
from PCApp.ui.register_window import RegisterWindow

from PCApp.ui.game_widget import GameView
from PCApp.ui.patient_dashboard import PatientDashboard
from PCApp.ui.doctor_dashboard import DoctorDashboard
from PCApp.ui.doctor_profile_view import DoctorProfileView
from PCApp.ui.patients_view import PatientsView
from PCApp.ui.calendar_view import CalendarView   # ✅ DODANE
from PCApp.ui.sidebar import Sidebar

from PCApp.api_client import APIClient


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.current_user = None  # jedyne źródło stanu usera

        self.sidebar = None
        self.doctor_dashboard = None
        self.doctor_profile_view = None
        self.patient_dashboard = None
        self.patients_view = None
        self.calendar_view = None   # ✅ DODANE

        self._setup_window()
        self._init_managers()
        self._init_ui()
        self._apply_focusly_style()

    # ================= OKNO =================

    def _setup_window(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
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

    def _init_ui(self):
        self.resize_handler = WindowResizeHandler(self)
        self._setup_tray_icon()

        central = QWidget()
        self.setCentralWidget(central)

        self.title_bar = TitleBar(self.theme, self.strings, self)
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize_restore)
        self.title_bar.settings_clicked.connect(self.show_settings)

        self.stacked = QStackedWidget()

        self.login_page = LoginPage(self.strings, self.api_client, self)
        self.login_page.login_successful.connect(self._handle_login_success)
<<<<<<< HEAD
=======
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.setCurrentWidget(self.login_page)

        self.game_view = GameView()
        self.game_view.finished.connect(self.on_game_finished)
        self.stacked_widget.addWidget(self.game_view)
>>>>>>> f2f1bd596c1cbaded743e65ccbabfcad552f4bd1

        self.register_page = RegisterWindow(self.api_client, self)
        self.register_page.back_to_login.connect(self.show_login)

        self.stacked.addWidget(self.login_page)
        self.stacked.addWidget(self.register_page)
        self.stacked.setCurrentWidget(self.login_page)

        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.stacked)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.title_bar)
        main_layout.addLayout(self.content_layout)

        self.settings_dialog = None

    # ================= LOGOWANIE =================

    def _handle_login_success(self, user_data: dict):
        self.current_user = user_data
        role = user_data.get("role")

        # cleanup
        for w in (
            self.sidebar,
            self.doctor_dashboard,
            self.doctor_profile_view,
            self.patient_dashboard,
            self.patients_view,
            self.calendar_view
        ):
            if w:
                w.setParent(None)
                w.deleteLater()

        self.sidebar = None
        self.doctor_dashboard = None
        self.doctor_profile_view = None
        self.patient_dashboard = None
        self.patients_view = None
        self.calendar_view = None

        if role == "doctor":
            self.sidebar = Sidebar(self)
            self.content_layout.insertWidget(0, self.sidebar)

            self.doctor_dashboard = DoctorDashboard(user_data, self)
            self.doctor_profile_view = DoctorProfileView(self)
            self.patients_view = PatientsView(self)
            self.calendar_view = CalendarView(self)   # ✅ DODANE

            self.stacked.addWidget(self.doctor_dashboard)
            self.stacked.addWidget(self.doctor_profile_view)
            self.stacked.addWidget(self.patients_view)
            self.stacked.addWidget(self.calendar_view)

            self.stacked.setCurrentWidget(self.doctor_dashboard)

        else:
            self.patient_dashboard = PatientDashboard(user_data, self)
            self.stacked.addWidget(self.patient_dashboard)
            self.stacked.setCurrentWidget(self.patient_dashboard)

    # ================= NAWIGACJA (SIDEBAR) =================

    def show_doctor_dashboard(self):
        if self.doctor_dashboard:
            self.stacked.setCurrentWidget(self.doctor_dashboard)

    def show_doctor_profile(self):
        if self.doctor_profile_view:
            self.stacked.setCurrentWidget(self.doctor_profile_view)

    def show_patients(self):
        if self.patients_view:
            self.stacked.setCurrentWidget(self.patients_view)

    def show_calendar(self):
        if self.calendar_view:
            self.stacked.setCurrentWidget(self.calendar_view)

    def show_login(self):
        if self.sidebar:
            self.sidebar.setParent(None)
            self.sidebar.deleteLater()
            self.sidebar = None
        self.stacked.setCurrentWidget(self.login_page)

    def logout(self):
        self.current_user = None
        self.show_login()

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
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(
                self.settings, self.strings, self.theme, self
            )
        self.settings_dialog.show()

    # ================= TRAY =================

    def _setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        menu = QMenu(self)
        menu.addAction(QAction("Quit", self, triggered=QApplication.quit))
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    # ================= OKNO =================

    def toggle_maximize_restore(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    # ================= STYL =================

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
        """)
