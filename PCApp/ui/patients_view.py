from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem,
    QFrame
)
from PyQt6.QtCore import Qt
from datetime import date
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
PATIENTS_PATH = BASE_DIR / "data" / "patients.json"


class PatientsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._setup_ui()
        self._load_patients()

    # ================= UI =================

    def _setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(20)

        # ===== TITLE =====
        title = QLabel("Moi pacjenci")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: white;
        """)
        main.addWidget(title)

        # ===== SEARCH =====
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Wyszukaj pacjenta")
        self.search.textChanged.connect(self._filter)
        self.search.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.15);
                color: white;
                border-radius: 14px;
                padding: 12px 16px;
                font-size: 14px;
                border: 1px solid rgba(255,255,255,0.25);
            }
            QLineEdit::placeholder {
                color: rgba(255,255,255,0.7);
            }
        """)
        main.addWidget(self.search)

        # ===== GRADIENT CARD =====
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

        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(20, 20, 20, 20)
        inner_layout.setSpacing(16)

        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Imię", "Nazwisko", "Wiek", "Status"
        ])

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                color: white;
                gridline-color: rgba(255,255,255,0.2);
                border: none;
            }

            QHeaderView::section {
                background: rgba(255,255,255,0.15);
                color: white;
                padding: 10px;
                font-weight: 700;
                border: 1px solid rgba(255,255,255,0.25);
            }

            QTableWidget::item {
                padding: 10px;
                border: 1px solid rgba(255,255,255,0.2);
            }

            QTableWidget::item:selected {
                background: rgba(255,255,255,0.25);
            }

            QTableWidget::item:hover {
                background: rgba(255,255,255,0.15);
            }
        """)

        inner_layout.addWidget(self.table)
        main.addWidget(card)

    # ================= DATA =================

    def _load_patients(self):
        self.patients = []

        if PATIENTS_PATH.exists():
            with open(PATIENTS_PATH, "r", encoding="utf-8") as f:
                self.patients = list(json.load(f).values())

        self._render(self.patients)

    def _render(self, patients):
        self.table.setRowCount(len(patients))

        for row, p in enumerate(patients):
            self.table.setItem(row, 0, QTableWidgetItem(p["first_name"]))
            self.table.setItem(row, 1, QTableWidgetItem(p["last_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(
                str(self._age(p["birth_date"]))
            ))
            self.table.setItem(row, 3, QTableWidgetItem("Aktywny"))

        self.visible_patients = patients

    # ================= FILTER =================

    def _filter(self, text):
        t = text.lower().strip()
        filtered = [
            p for p in self.patients
            if t in f"{p['first_name']} {p['last_name']}".lower()
        ]
        self._render(filtered)

    # ================= HELPERS =================

    def _age(self, birth):
        y, m, d = map(int, birth.split("-"))
        today = date.today()
        return today.year - y - ((today.month, today.day) < (m, d))
