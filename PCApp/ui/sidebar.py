from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt


class Sidebar(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        self.setFixedWidth(220)
        self.setObjectName("sidebar")

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Focusly")
        title.setObjectName("sidebarTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addSpacing(20)

        dashboard_btn = QPushButton("🏠 Dashboard")
        dashboard_btn.clicked.connect(
            lambda: self.main_window.show_doctor_dashboard()
        )

        profile_btn = QPushButton("🩺 Profil lekarza")
        profile_btn.clicked.connect(
            lambda: self.main_window.show_doctor_profile()
        )

        settings_btn = QPushButton("⚙️ Ustawienia konta")
        settings_btn.clicked.connect(
            self.main_window.show_settings
        )

        logout_btn = QPushButton("🚪 Wyloguj")
        logout_btn.clicked.connect(
            self.main_window.logout
        )

        for btn in (dashboard_btn, profile_btn, settings_btn, logout_btn):
            btn.setObjectName("sidebarButton")
            layout.addWidget(btn)

        layout.addStretch()

    def _apply_style(self):
        self.setStyleSheet("""
        QWidget#sidebar {
            background: rgba(0, 0, 0, 0.35);
        }

        QLabel#sidebarTitle {
            color: white;
            font-size: 22px;
            font-weight: bold;
        }

        QPushButton#sidebarButton {
            background: transparent;
            color: white;
            border: none;
            text-align: left;
            padding: 12px;
            font-size: 15px;
            border-radius: 10px;
        }

        QPushButton#sidebarButton:hover {
            background: rgba(255, 255, 255, 0.15);
        }
        """)
