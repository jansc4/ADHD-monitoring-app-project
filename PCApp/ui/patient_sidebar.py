from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel
)
from PyQt6.QtCore import Qt


class PatientSidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("patientSidebar")

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 24, 18, 24)
        layout.setSpacing(14)

        title = QLabel("Focusly")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("sidebarTitle")

        self.dashboard_btn = QPushButton("🏠 Dashboard")
        self.dashboard_btn.clicked.connect(
            lambda: self.window().show_patient_dashboard()
        )

        self.survey_btn = QPushButton("📝 Ankieta dzienna")
        self.survey_btn.clicked.connect(
            lambda: self.window().show_patient_survey()
        )

        self.game_btn = QPushButton("🎮 Gra terapeutyczna")
        self.game_btn.clicked.connect(
            lambda: self.window().start_game()
        )

        self.history_btn = QPushButton("📊 Historia")
        self.history_btn.clicked.connect(
            lambda: self.window().show_patient_dashboard()
        )

        self.settings_btn = QPushButton("⚙️ Ustawienia")
        self.settings_btn.clicked.connect(
            lambda: self.window().show_settings()
        )

        self.logout_btn = QPushButton("🚪 Wyloguj")
        self.logout_btn.clicked.connect(
            lambda: self.window().logout()
        )

        for btn in (
            self.dashboard_btn,
            self.survey_btn,
            self.game_btn,
            self.history_btn,
            self.settings_btn,
            self.logout_btn
        ):
            btn.setObjectName("sidebarButton")

        layout.addWidget(title)
        layout.addSpacing(12)

        layout.addWidget(self.dashboard_btn)
        layout.addWidget(self.survey_btn)
        layout.addWidget(self.game_btn)
        layout.addWidget(self.history_btn)
        layout.addWidget(self.settings_btn)

        layout.addStretch()
        layout.addWidget(self.logout_btn)

    def _apply_style(self):
        self.setStyleSheet("""
        QWidget#patientSidebar {
            background: rgba(8, 10, 20, 0.85);
            border-right: 1px solid rgba(120,120,255,140);
        }

        QLabel#sidebarTitle {
            font-size: 22px;
            font-weight: bold;
            color: white;
            margin-bottom: 12px;
        }

        QPushButton#sidebarButton {
            background: rgba(20, 20, 40, 200);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 12px 16px;
            text-align: left;
            font-size: 15px;
        }

        QPushButton#sidebarButton:hover {
            background: rgba(80, 80, 160, 220);
        }
        """)
