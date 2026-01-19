from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QTimeEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTime
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
MEDS_PATH = BASE_DIR / "data" / "medications.json"


class PatientSurveyView(QWidget):
    def __init__(self, user_data: dict, parent=None):
        super().__init__(parent)
        self.user_data = user_data

        self._setup_ui()
        self._load_medications()
        self._apply_style()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(18)

        title = QLabel("Ankieta dzienna")
        title.setObjectName("dashboardTitle")

        self.med_combo = QComboBox()
        self.med_combo.setObjectName("surveyInput")
        self.med_combo.addItem("— wybierz lek —", None)

        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")

        self.mood_text = QTextEdit()
        self.mood_text.setPlaceholderText("Jak się dziś czujesz? Opisz swoje samopoczucie...")

        self.save_btn = QPushButton("Zapisz ankietę")
        self.save_btn.setObjectName("primaryButton")
        self.save_btn.clicked.connect(self._save_survey)

        main_layout.addWidget(title)
        main_layout.addWidget(QLabel("Jaki lek przyjąłeś?"))
        main_layout.addWidget(self.med_combo)
        main_layout.addWidget(QLabel("Godzina przyjęcia"))
        main_layout.addWidget(self.time_edit)
        main_layout.addWidget(QLabel("Samopoczucie"))
        main_layout.addWidget(self.mood_text)
        main_layout.addWidget(self.save_btn)
        main_layout.addStretch()

    def _load_medications(self):
        if not MEDS_PATH.exists():
            return

        with open(MEDS_PATH, "r", encoding="utf-8") as f:
            meds = json.load(f)

        for m in meds:
            self.med_combo.addItem(m["name"], m["id"])

    def _save_survey(self):
        if self.med_combo.currentData() is None:
            QMessageBox.warning(self, "Błąd", "Wybierz lek")
            return

        if not self.mood_text.toPlainText().strip():
            QMessageBox.warning(self, "Błąd", "Opisz swoje samopoczucie")
            return

        QMessageBox.information(self, "Zapisano", "Ankieta zapisana ✔")

    def _apply_style(self):
        self.setStyleSheet("""
        QLabel#dashboardTitle {
            font-size: 26px;
            font-weight: bold;
            color: white;
        }

        QComboBox#surveyInput,
        QTimeEdit,
        QTextEdit {
            background-color: rgba(10, 10, 25, 200);
            border: 1px solid rgba(120,120,255,140);
            border-radius: 10px;
            padding: 10px;
            color: white;
        }

        QPushButton#primaryButton {
            background: #6c63ff;
            color: white;
            padding: 12px;
            border-radius: 14px;
        }
        """)
