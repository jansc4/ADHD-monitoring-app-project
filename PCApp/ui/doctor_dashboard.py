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
    def __init__(self, user_data: dict, parent=None):
        super().__init__(parent)
        self.user_data = user_data

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
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)

        subheader = QLabel("Panel lekarza • zarządzanie pacjentami i sesjami")
        subheader.setObjectName("dashboardSubHeader")
        subheader.setAlignment(Qt.AlignmentFlag.AlignLeft)

        main_layout.addWidget(header)
        main_layout.addWidget(subheader)

        # ================= STAT CARDS =================
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(24)

        patients_card = StatCard("👥 Liczba pacjentów", "—")
        sessions_card = StatCard("📊 Sesje dzisiaj", "—")
        alerts_card = StatCard("⚠️ Alerty", "—")

        cards_layout.addWidget(patients_card)
        cards_layout.addWidget(sessions_card)
        cards_layout.addWidget(alerts_card)

        main_layout.addLayout(cards_layout)

        # ================= ACTION BUTTONS =================
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        patients_btn = QPushButton("👥 Lista pacjentów")
        patients_btn.setObjectName("secondaryButton")

        stats_btn = QPushButton("📈 Statystyki")
        stats_btn.setObjectName("secondaryButton")

        buttons_layout.addWidget(patients_btn)
        buttons_layout.addWidget(stats_btn)
        buttons_layout.addStretch()

        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()

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
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 8px;
        }

        QPushButton#secondaryButton {
            background: rgba(255, 255, 255, 0.15);
            color: white;
            border-radius: 20px;
            padding: 14px 20px;
            font-size: 15px;
        }

        QPushButton#secondaryButton:hover {
            background: rgba(255, 255, 255, 0.25);
        }
        """)
