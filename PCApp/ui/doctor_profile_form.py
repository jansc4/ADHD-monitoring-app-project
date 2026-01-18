from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QMessageBox, QScrollArea
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DOCTORS_PATH = BASE_DIR / "data" / "doctors.json"
CITIES_PATH = BASE_DIR / "data" / "cities.json"


class DoctorProfileForm(QWidget):
    profile_saved = pyqtSignal()

    def __init__(self, email: str, parent=None):
        super().__init__(parent)

        if not email:
            raise RuntimeError("Brak emaila lekarza")

        self.email = email.strip().lower()

        self._setup_ui()
        self._load_existing_profile()

    # ================= UI =================
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # --- SCROLL ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)

        self.facility = QComboBox()
        self.facility.addItems([
            "— wybierz placówkę —",
            "Samodzielna praktyka",
            "Przychodnia",
            "Szpital",
            "Centrum medyczne",
            "Prywatny gabinet"
        ])

        self.specialization = QComboBox()
        self.specialization.addItems([
            "— wybierz specjalizację —",
            "Neurolog",
            "Psychiatra",
            "Psycholog kliniczny",
            "Pediatra",
            "Lekarz rodzinny",
            "Rehabilitant"
        ])

        self.pwz = QLineEdit()
        self.pwz.setPlaceholderText("Numer PWZ (7 cyfr)")
        self.pwz.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"\d{7}"))
        )

        self.postal_code = QLineEdit()
        self.postal_code.setPlaceholderText("Kod pocztowy (np. 20-005)")
        self.postal_code.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"\d{2}-\d{3}"))
        )
        self.postal_code.textChanged.connect(self._load_cities)

        self.city = QComboBox()
        self.city.addItem("— wybierz miejscowość —")
        self.city.setEnabled(False)

        self.save_btn = QPushButton("Zapisz profil")
        self.save_btn.clicked.connect(self._save_profile)

        for label, widget in [
            ("Placówka", self.facility),
            ("Specjalizacja", self.specialization),
            ("PWZ", self.pwz),
            ("Kod pocztowy", self.postal_code),
            ("Miejscowość", self.city)
        ]:
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)

        layout.addWidget(self.save_btn)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    # ================= MIASTA =================
    def _load_cities(self):
        code = self.postal_code.text().strip()

        self.city.clear()
        self.city.addItem("— wybierz miejscowość —")
        self.city.setEnabled(False)

        if not QRegularExpression(r"\d{2}-\d{3}").match(code).hasMatch():
            return

        if not CITIES_PATH.exists():
            QMessageBox.warning(self, "Błąd", "Brak pliku cities.json")
            return

        try:
            with open(CITIES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Błąd", "Błędny format cities.json")
            return

        cities = data.get(code)

        if not cities or not isinstance(cities, list):
            return

        self.city.setEnabled(True)
        for city in cities:
            self.city.addItem(city)

    # ================= DATA =================
    def _load_existing_profile(self):
        if not DOCTORS_PATH.exists():
            return

        with open(DOCTORS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        doctor = data.get(self.email)
        if not doctor:
            return

        def set_combo(combo, value):
            if not value:
                return
            i = combo.findText(value)
            if i >= 0:
                combo.setCurrentIndex(i)

        set_combo(self.facility, doctor.get("facility"))
        set_combo(self.specialization, doctor.get("specialization"))

        self.pwz.setText(doctor.get("pwz", ""))
        self.postal_code.setText(doctor.get("postal_code", ""))

        self._load_cities()
        set_combo(self.city, doctor.get("city"))

    # ================= SAVE =================
    def _save_profile(self):
        if (
            self.facility.currentIndex() == 0
            or self.specialization.currentIndex() == 0
            or not self.pwz.hasAcceptableInput()
            or self.city.currentIndex() == 0
        ):
            QMessageBox.warning(self, "Błąd", "Uzupełnij wszystkie dane")
            return

        DOCTORS_PATH.parent.mkdir(parents=True, exist_ok=True)

        data = {}
        if DOCTORS_PATH.exists():
            with open(DOCTORS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

        data[self.email] = {
            "facility": self.facility.currentText(),
            "specialization": self.specialization.currentText(),
            "pwz": self.pwz.text(),
            "postal_code": self.postal_code.text(),
            "city": self.city.currentText(),
            "profile_completed": True
        }

        with open(DOCTORS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        QMessageBox.information(self, "Zapisano", "Profil zapisany")
        self.profile_saved.emit()

    # ================= STYLE =================
    def _apply_style(self):
        self.setStyleSheet("""
        QLabel#profileTitle {
            font-size: 22px;
            font-weight: bold;
            color: white;
        }
        QLabel#profileSubtitle {
            color: rgba(255,255,255,0.65);
        }
        QLineEdit#profileInput,
        QComboBox#profileInput {
            background: white;
            border-radius: 20px;
            padding: 12px;
        }
        QPushButton#primaryButton {
            background: #6c63ff;
            color: white;
            padding: 14px;
            border-radius: 22px;
        }
        """)

