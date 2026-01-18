from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt


class PatientProfileView(QWidget):
    def __init__(self, patient: dict, parent=None):
        super().__init__(parent)
        self.patient = patient
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 18px;
                padding: 24px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        title = QLabel(
            f"{self.patient.get('first_name')} {self.patient.get('last_name')}"
        )
        title.setStyleSheet("font-size:24px;font-weight:700;")

        birth = QLabel(f"Data urodzenia: {self.patient.get('birth_date')}")
        gender = QLabel(f"Płeć: {self.patient.get('gender', '—')}")
        status = QLabel("Status: aktywny")

        for w in (birth, gender, status):
            w.setStyleSheet("font-size:14px;color:#444;")

        card_layout.addWidget(title)
        card_layout.addWidget(birth)
        card_layout.addWidget(gender)
        card_layout.addWidget(status)

        layout.addWidget(card)
        layout.addStretch()
