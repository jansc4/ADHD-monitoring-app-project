from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout
)
from PyQt6.QtCore import Qt

from PCApp.ui.components.stat_card.stat_card import StatCard


class PatientDashboard(QWidget):
    def __init__(self, user_data: dict, parent=None):
        super().__init__(parent)
        self.user_data = user_data

        self.setObjectName("patientDashboard")
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(32)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # ================= HEADER =================
        header = QLabel(
            f"Witaj, {self.user_data.get('name', 'Pacjencie')} 👋"
        )
        header.setObjectName("dashboardHeader")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(header)

        # ================= STAT CARDS =================
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(24)

        focus_card = StatCard("⏱️ Czas skupienia", "brak danych")
        breaks_card = StatCard("☕ Liczba przerw", "brak danych")
        concentration_card = StatCard("🧠 Poziom koncentracji", "brak danych")

        cards_layout.addWidget(focus_card)
        cards_layout.addWidget(breaks_card)
        cards_layout.addWidget(concentration_card)

        main_layout.addLayout(cards_layout)

        # ================= BUTTONS =================
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        start_btn = QPushButton("▶ Rozpocznij sesję")
        start_btn.setObjectName("primaryButton")

        history_btn = QPushButton("📁 Historia sesji")
        history_btn.setObjectName("secondaryButton")

        buttons_layout.addWidget(start_btn)
        buttons_layout.addWidget(history_btn)

        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()

    def _apply_style(self):
        self.setStyleSheet("""
        QWidget#patientDashboard {
            background: transparent;
        }

        QLabel#dashboardHeader {
            font-size: 28px;
            font-weight: bold;
            color: white;
        }

        QPushButton#primaryButton {
            background: #6c63ff;
            color: white;
            border-radius: 20px;
            padding: 14px;
            font-size: 16px;
            font-weight: bold;
        }

        QPushButton#primaryButton:hover {
            background: #584fff;
        }

        QPushButton#secondaryButton {
            background: rgba(255, 255, 255, 0.15);
            color: white;
            border-radius: 20px;
            padding: 14px;
            font-size: 16px;
        }

        QPushButton#secondaryButton:hover {
            background: rgba(255, 255, 255, 0.25);
        }
        """)
