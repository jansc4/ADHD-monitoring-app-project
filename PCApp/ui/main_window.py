"""
Główne okno aplikacji.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QSystemTrayIcon, QMenu,
    QApplication, QStackedWidget,
    QMessageBox
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
from PCApp.ui.game_mode_dialog import GameModeDialog

from PCApp.ui.patient_dashboard import PatientDashboard
from PCApp.ui.patient_survey_view import PatientSurveyView
from PCApp.ui.doctor_dashboard import DoctorDashboard
from PCApp.ui.doctor_profile_view import DoctorProfileView
from PCApp.ui.patients_view import PatientsView
from PCApp.ui.calendar_view import CalendarView

from PCApp.ui.sidebar import Sidebar              # lekarz
from PCApp.ui.patient_sidebar import PatientSidebar  # pacjent

from PCApp.api_client import APIClient


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.current_user = None

        self.sidebar = None
        self.patient_sidebar = None

        self.doctor_dashboard = None
        self.doctor_profile_view = None
        self.patient_dashboard = None
        self.patient_survey_view = None
        self.patients_view = None
        self.calendar_view = None
        self.game_view = None

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
            self.settings.get("api_url") or "http://127.0.0.1:8001"
        )

    # ================= UI =================

    def _init_ui(self):
        self.resize_handler = WindowResizeHandler(self)
        self._setup_tray_icon()

        central = QWidget()
        central.setObjectName("CentralContainer")
        self.setCentralWidget(central)

        self.title_bar = TitleBar(self.theme, self.strings, self)
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize_restore)
        self.title_bar.settings_clicked.connect(self.show_settings)

        self.stacked = QStackedWidget()

        self.login_page = LoginPage(self.strings, self.api_client, self)
        self.login_page.login_successful.connect(self._handle_login_success)
        self.login_page.register_requested.connect(self.show_register)

        self.register_page = RegisterWindow(self.api_client, self)
        self.register_page.back_to_login.connect(self.show_login)

        self.game_settings = {
            "difficulty": "Średni",
            "trials": 20
        }
        self.game_view = GameView()
        self.game_view.finished.connect(self.on_game_finished)
        self.game_view.back_requested.connect(lambda: self._try_leave_game(self.show_patient_dashboard))

        self.stacked.addWidget(self.login_page)
        self.stacked.addWidget(self.register_page)
        self.stacked.addWidget(self.game_view)
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

        for w in (
            self.sidebar,
            self.patient_sidebar,
            self.doctor_dashboard,
            self.doctor_profile_view,
            self.patient_dashboard,
            self.patient_survey_view,
            self.patients_view,
            self.calendar_view
        ):
            if w:
                w.setParent(None)
                w.deleteLater()

        self.sidebar = None
        self.patient_sidebar = None
        self.doctor_dashboard = None
        self.doctor_profile_view = None
        self.patient_dashboard = None
        self.patient_survey_view = None
        self.patients_view = None
        self.calendar_view = None

        if role == "doctor":
            self.sidebar = Sidebar(self)
            self.content_layout.insertWidget(0, self.sidebar)

            self.doctor_dashboard = DoctorDashboard(user_data, self)
            self.doctor_profile_view = DoctorProfileView(self)
            self.patients_view = PatientsView(self)
            self.calendar_view = CalendarView(self)

            self.stacked.addWidget(self.doctor_dashboard)
            self.stacked.addWidget(self.doctor_profile_view)
            self.stacked.addWidget(self.patients_view)
            self.stacked.addWidget(self.calendar_view)

            self.stacked.setCurrentWidget(self.doctor_dashboard)

        else:
            self.patient_sidebar = PatientSidebar(self)
            self.content_layout.insertWidget(0, self.patient_sidebar)

            self.patient_dashboard = PatientDashboard(user_data, self)
            self.patient_survey_view = PatientSurveyView(user_data, self)

            self.stacked.addWidget(self.patient_dashboard)
            self.stacked.addWidget(self.patient_survey_view)

            self.stacked.setCurrentWidget(self.patient_dashboard)

    def show_register(self):
        self.stacked.setCurrentWidget(self.register_page)

    # ================= NAWIGACJA =================

    def show_patient_dashboard(self):
        if not self.patient_dashboard:
            return
        self._try_leave_game(lambda: self.stacked.setCurrentWidget(self.patient_dashboard))

    def show_patient_survey(self):
        if not self.patient_survey_view:
            return
        self._try_leave_game(lambda: self.stacked.setCurrentWidget(self.patient_survey_view))

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

        if self.patient_sidebar:
            self.patient_sidebar.setParent(None)
            self.patient_sidebar.deleteLater()
            self.patient_sidebar = None

        self.stacked.setCurrentWidget(self.login_page)

    def logout(self):
        in_game = (
                self.stacked.currentWidget() == self.game_view
                and getattr(self.game_view, "is_running", False)
        )

        if in_game:
            self.game_view.pause_game()

        text = "Czy na pewno chcesz się wylogować?"
        if in_game:
            text += "\n\nJeśli wyjdziesz teraz, Twój wynik z gry nie zostanie zapisany."

        confirmed = self._confirm_dialog("Wylogować?", text, "Tak", "Nie")

        if confirmed:
            if in_game:
                self.game_view.abort_game()
            self.current_user = None
            self.show_login()
        else:
            if in_game:
                self.game_view.resume_game()

    # ================= GRA =================

    def show_game_menu(self):
        """Wyświetla okno wyboru trybu i ustawień przed rozpoczęciem gry."""
        dialog = GameModeDialog(self, initial_settings=self.game_settings)

        dialog.start_btn.clicked.connect(lambda: self._start_game_from_menu(dialog))
        dialog.survey_btn.clicked.connect(lambda: self._start_survey_from_menu(dialog))

        dialog.settings_saved.connect(self._update_game_settings)

        dialog.exec()

    def apply_game_settings(self, game_view):
        """Stosuje zapisane ustawienia gry do widoku gry."""

        difficulty = self.game_settings.get("difficulty", "Średni")
        trials = int(self.game_settings.get("trials", 20))

        game_view.set_difficulty(difficulty)

        game_view.max_trials = trials

        if difficulty == "Łatwy":
            game_view.trial_time_limit_ms = 1500
            game_view.iti_ms = 450
        elif difficulty == "Średni":
            game_view.trial_time_limit_ms = 1200
            game_view.iti_ms = 350
        elif difficulty == "Trudny":
            game_view.trial_time_limit_ms = 900
            game_view.iti_ms = 250

    def _update_game_settings(self, s: dict):
        """"Aktualizuje zapisane ustawienia gry na podstawie danych z menu."""
        self.game_settings = s

    def start_game(self):
        """Stosuje ustawienia i rozpoczyna nową sesję gry."""

        self.apply_game_settings(self.game_view)
        self.game_view.start_game()
        self.stacked.setCurrentWidget(self.game_view)

    def on_game_finished(self, result):
        """Obsługuje zakończenie gry i przełącza widok po jej zakończeniu."""

        print("Wynik gry:", result)
        if self.patient_dashboard:
            self.stacked.setCurrentWidget(self.patient_dashboard)
        else:
            self.stacked.setCurrentWidget(self.login_page)

    def _start_game_from_menu(self, dialog):
        """Zamyka menu gry i rozpoczyna grę."""
        dialog.accept()
        self.start_game()

    def _start_survey_from_menu(self, dialog):
        """Zamyka menu gry i przechodzi do ankiety pacjenta."""
        dialog.accept()
        self.show_patient_survey()

    def _try_leave_game(self, go_to_callable):
        """Obsługuje próbę opuszczenia gry w trakcie sesji."""

        # jeśli nie jesteśmy w grze lub gra nie trwa – normalnie idź dalej
        if self.stacked.currentWidget() != self.game_view or not self.game_view.is_running:
            go_to_callable()
            return

        # pauzuj i pytaj
        self.game_view.pause_game()

        confirmed = self._confirm_dialog(
            "Wyjść z gry?",
            "Czy na pewno chcesz wyjść? Twój wynik nie zostanie zapisany.",
            "Tak",
            "Nie"
        )

        if confirmed:
            self.game_view.abort_game()
            go_to_callable()
        else:
            self.game_view.resume_game()

    # ============== OKNO ZAPYTANIA ================

    def _confirm_dialog(self, title: str, text: str, yes_text: str = "Tak", no_text: str = "Nie") -> bool:
        """Wyświetla okno potwierdzenia z przyciskami Tak/Nie i zwraca decyzję użytkownika."""

        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Question)

        yes_btn = msg.addButton(yes_text, QMessageBox.ButtonRole.YesRole)
        no_btn = msg.addButton(no_text, QMessageBox.ButtonRole.NoRole)
        msg.setDefaultButton(no_btn)

        # spójny styl (ciemny, zaokrąglony, podobny do Twojego UI)
        msg.setStyleSheet("""
            QMessageBox {
                background: rgba(10, 10, 40, 0.98);
                color: white;
                font-size: 14px;
            }
            QLabel {
                color: rgba(255,255,255,0.92);
                font-size: 14px;
            }
            QPushButton {
                background: rgba(255,255,255,0.12);
                border: 1px solid rgba(255,255,255,0.18);
                padding: 8px 14px;
                border-radius: 12px;
                min-width: 90px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.18);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.10);
            }
        """)

        msg.exec()
        return msg.clickedButton() == yes_btn

    # ================= USTAWIENIA =================

    def show_settings(self):
        if self.stacked.currentWidget() == self.game_view and getattr(self.game_view, "is_running", False):
            self.game_view.pause_game()

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
            background: none;
        }

        #CentralContainer {
            background: qlineargradient(
                x1:0, y1:0,
                x2:1, y2:1,
                stop:0 #020024,
                stop:0.4 #090979,
                stop:1 #3f32ff
            );
        }

        QWidget {
            background: transparent;
            color: #ffffff;
        }

        QFrame, QStackedWidget {
            background: transparent;
        }
        """)
