from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QFrame, QTabWidget, QTableWidget,
    QTableWidgetItem
)
from PyQt6.QtCore import Qt


class PatientDashboard(QWidget):
    def __init__(self, user_data: dict, parent=None):
        super().__init__(parent)
        self.user_data = user_data

        self._setup_ui()
        self._apply_style()

    # ================= UI =================

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        title = QLabel("Panel pacjenta")
        title.setObjectName("dashboardTitle")

        self.game_card = self._create_game_card()
        self.history_card = self._create_history_card()

        main_layout.addWidget(title)
        main_layout.addWidget(self.game_card)
        main_layout.addWidget(self.history_card)
        main_layout.addStretch()

    # ================= KARTY =================

    def _create_card(self, title_text):
        frame = QFrame()
        frame.setObjectName("dashboardCard")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        title = QLabel(title_text)
        title.setObjectName("cardTitle")

        layout.addWidget(title)

        return frame, layout

    def _create_game_card(self):
        frame, layout = self._create_card("Gra terapeutyczna")

        desc = QLabel("Trening koncentracji – reaguj jak najszybciej na cele.")
        desc.setWordWrap(True)

        last_result = QLabel("Ostatni wynik: 82 pkt • Śr. czas reakcji: 610 ms")
        last_result.setObjectName("subtleText")

        self.start_game_btn = QPushButton("Rozpocznij grę")
        self.start_game_btn.setObjectName("primaryButton")
        self.start_game_btn.clicked.connect(self._start_game)

        layout.addWidget(desc)
        layout.addWidget(last_result)
        layout.addWidget(self.start_game_btn)

        return frame

    def _create_history_card(self):
        frame, layout = self._create_card("Historia")

        tabs = QTabWidget()
        tabs.setObjectName("historyTabs")

        # --- TAB: Ankiety ---
        self.survey_table = QTableWidget(0, 4)
        self.survey_table.setHorizontalHeaderLabels([
            "Data", "Lek", "Godzina", "Samopoczucie"
        ])
        self._mock_survey_data()

        # --- TAB: Gry ---
        self.game_table = QTableWidget(0, 4)
        self.game_table.setHorizontalHeaderLabels([
            "Data", "Trafienia", "Śr. czas reakcji", "Wynik"
        ])
        self._mock_game_data()

        tabs.addTab(self.survey_table, "Ankiety")
        tabs.addTab(self.game_table, "Gry")

        layout.addWidget(tabs)

        return frame

    # ================= MOCK =================

    def _mock_survey_data(self):
        data = [
            ("2026-01-17", "Medikinet", "08:30", "Czuję się dobrze."),
            ("2026-01-16", "—", "—", "Rozdrażniony.")
        ]

        self.survey_table.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, val in enumerate(row):
                self.survey_table.setItem(r, c, QTableWidgetItem(val))

    def _mock_game_data(self):
        data = [
            ("2026-01-17", "34", "612 ms", "82"),
            ("2026-01-16", "28", "689 ms", "74")
        ]

        self.game_table.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, val in enumerate(row):
                self.game_table.setItem(r, c, QTableWidgetItem(val))

    # ================= AKCJE =================

    def _start_game(self):
        if hasattr(self.parent(), "show_game_menu"):
            self.parent().show_game_menu()

    # ================= STYL =================

    def _apply_style(self):
        self.setStyleSheet("""
        QLabel#dashboardTitle {
            font-size: 26px;
            font-weight: bold;
            color: white;
        }

        QFrame#dashboardCard {
            background-color: rgba(20, 20, 40, 200);
            border: 1px solid rgba(120, 120, 255, 180);
            border-radius: 16px;
        }

        QLabel#cardTitle {
            font-size: 18px;
            font-weight: bold;
            color: #cfd3ff;
        }

        QLabel#subtleText {
            color: rgba(255,255,255,0.75);
        }

        QTabWidget::pane {
            border: 1px solid rgba(120,120,255,140);
            border-radius: 10px;
            background-color: rgba(10, 10, 25, 200);
        }

        QTabBar::tab {
            background: rgba(20, 20, 40, 200);
            color: white;
            padding: 8px 14px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 4px;
        }

        QTabBar::tab:selected {
            background: rgba(60, 60, 120, 220);
        }

        QTableWidget {
            background-color: rgba(10, 10, 25, 200);
            border: none;
            color: white;
            gridline-color: rgba(120,120,255,80);
        }

        QHeaderView::section {
            background-color: rgba(30, 30, 60, 200);
            color: white;
            border: none;
            padding: 6px;
        }

        QPushButton#primaryButton {
            background: #6c63ff;
            color: white;
            padding: 10px 16px;
            border-radius: 12px;
        }

        QPushButton#primaryButton:hover {
            background: #7d75ff;
        }
        """)
