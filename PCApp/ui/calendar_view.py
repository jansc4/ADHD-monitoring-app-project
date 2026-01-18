from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QCalendarWidget, QListWidget, QListWidgetItem,
    QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt, QDate
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
VISITS_PATH = BASE_DIR / "data" / "visits.json"


class CalendarView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_visits()

    # ================= UI =================

    def _setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(20)

        # ===== TITLE =====
        title = QLabel("Kalendarz wizyt")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: white;
        """)
        main.addWidget(title)

        # ===== GRADIENT CONTAINER =====
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                border-radius: 26px;
                padding: 2px;
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:1,
                    stop:0 #020024,
                    stop:0.4 #090979,
                    stop:1 #3f32ff
                );
            }
        """)

        inner = QFrame()
        inner.setStyleSheet("""
            QFrame {
                background: transparent;
                border-radius: 24px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.addWidget(inner)

        inner_layout = QHBoxLayout(inner)
        inner_layout.setContentsMargins(28, 28, 28, 28)
        inner_layout.setSpacing(32)

        # ===== CALENDAR =====
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )
        self.calendar.selectionChanged.connect(self._on_date_changed)

        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background: transparent;
                border: none;
            }

            /* MONTH / YEAR HEADER */
            QCalendarWidget QToolButton {
                color: white;
                font-size: 16px;
                font-weight: 700;
                background: transparent;
                border: none;
                margin: 6px;
            }

            /* WEEK DAYS */
            QCalendarWidget QHeaderView::section {
                background: transparent;
                color: white;
                font-weight: 600;
                border: none;
                padding: 6px;
            }

            /* DAYS GRID */
            QCalendarWidget QAbstractItemView {
                background: transparent;
                color: white;
                font-size: 14px;
                outline: 0;
                selection-background-color: rgba(255,255,255,0.25);
                selection-color: white;
            }

            /* EACH DAY CELL */
            QCalendarWidget QAbstractItemView::item {
                border: 1px solid rgba(255,255,255,0.25);
                border-radius: 6px;
                padding: 6px;
            }

            /* HOVER */
            QCalendarWidget QAbstractItemView::item:hover {
                background: rgba(255,255,255,0.15);
            }
        """)

        # ===== VISITS PANEL =====
        right = QVBoxLayout()
        right.setSpacing(14)

        visits_title = QLabel("Wizyty w wybranym dniu")
        visits_title.setStyleSheet("""
            font-size: 17px;
            font-weight: 700;
            color: white;
        """)

        self.visits = QListWidget()
        self.visits.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
                color: white;
            }
            QListWidget::item {
                background: rgba(255,255,255,0.15);
                border-radius: 14px;
                padding: 12px;
                margin-bottom: 8px;
                font-size: 14px;
                color: white;
            }
        """)

        right.addWidget(visits_title)
        right.addWidget(self.visits)

        inner_layout.addWidget(self.calendar, 2)
        inner_layout.addLayout(right, 1)

        main.addWidget(card)

    # ================= DATA =================

    def _load_visits(self):
        self.visits_data = []

        if VISITS_PATH.exists():
            with open(VISITS_PATH, "r", encoding="utf-8") as f:
                self.visits_data = json.load(f)

        self._show_visits_for_date(self.calendar.selectedDate())

    # ================= LOGIC =================

    def _on_date_changed(self):
        self._show_visits_for_date(self.calendar.selectedDate())

    def _show_visits_for_date(self, qdate: QDate):
        self.visits.clear()
        date_str = qdate.toString("yyyy-MM-dd")

        day_visits = [
            v for v in self.visits_data if v["date"] == date_str
        ]

        if not day_visits:
            item = QListWidgetItem("Brak wizyt")
            item.setForeground(Qt.GlobalColor.white)
            self.visits.addItem(item)
            return

        for v in day_visits:
            self.visits.addItem(
                f"{v['time']}  •  {v['patient_name']}"
            )
