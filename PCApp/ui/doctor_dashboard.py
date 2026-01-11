from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton
)
from PyQt6.QtCore import Qt

from PCApp.ui.components.stat_card.stat_card import StatCard


class DoctorDashboard(QWidget):
    def __init__(self, user_data: dict, main_window, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.main_window = main_window

        self.setObjectName("doctorDashboard")
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(32)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # ================= HEADER =================
        email = self.user_data.get("email", "lekarzu")

        header = QLabel(f"Witaj, <span style='color:#d6d3ff'>{email}</span> 👋")
        header.setObjectName("dashboardHeader")

        subheader = QLabel("Zarządzanie pacjentami i sesjami")
        subheader.setObjectName("dashboardSubHeader")

        main_layout.addWidget(header)
        main_layout.addWidget(subheader)

        # ================= STAT CARDS =================
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(24)

        cards_layout.addWidget(StatCard("👥 Pacjenci", "—"))
        cards_layout.addWidget(StatCard("📊 Sesje dziś", "—"))
        cards_layout.addWidget(StatCard("⚠️ Alerty", "—"))

        main_layout.addLayout(cards_layout)

        # ================= BUTTONS =================
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        profile_btn = QPushButton("🩺 Uzupełnij dane zawodowe")
        profile_btn.setObjectName("secondaryButton")
        profile_btn.clicked.connect(self._open_profile)

        buttons_layout.addWidget(profile_btn)
        buttons_layout.addStretch()

        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()

    def _open_profile(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.doctor_profile_view
        )

    def _apply_style(self):
        self.setStyleSheet("""
        QWidget#doctorDashboard {
            background: transparent;
        }

        QLabel#dashboardHeader {
            font-size: 28px;
            font-weight: bold;
            color: white;
        }

        QLabel#dashboardSubHeader {
            font-size: 15px;
            color: rgba(255,255,255,0.7);
            margin-bottom: 8px;
        }

        QPushButton#secondaryButton {
            background: rgba(255,255,255,0.15);
            color: white;
            border-radius: 20px;
            padding: 14px 20px;
            font-size: 15px;
        }

        QPushButton#secondaryButton:hover {
            background: rgba(255,255,255,0.25);
        }
        """)
