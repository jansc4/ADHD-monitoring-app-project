from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout
)
from PyQt6.QtCore import Qt


class DoctorProfileView(QWidget):
    def __init__(self, user_data: dict, main_window, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.main_window = main_window

        self.setObjectName("doctorProfileView")
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # ================= HEADER =================
        header = QLabel("Uzupełnij dane zawodowe 🩺")
        header.setObjectName("profileHeader")

        subheader = QLabel(
            "Te informacje będą widoczne tylko dla systemu i administratora."
        )
        subheader.setObjectName("profileSubHeader")

        main_layout.addWidget(header)
        main_layout.addWidget(subheader)

        # ================= FORM =================
        self.facility_input = QLineEdit(placeholderText="Placówka medyczna")
        self.specialization_input = QLineEdit(placeholderText="Specjalizacja")
        self.pwz_input = QLineEdit(placeholderText="Numer PWZ")
        self.city_input = QLineEdit(placeholderText="Miasto")

        for field in (
            self.facility_input,
            self.specialization_input,
            self.pwz_input,
            self.city_input
        ):
            field.setObjectName("profileInput")
            main_layout.addWidget(field)

        # ================= BUTTONS =================
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Zapisz dane")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save_profile)

        back_btn = QPushButton("← Wróć do dashboardu")
        back_btn.setObjectName("secondaryButton")
        back_btn.clicked.connect(self._go_back)

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(back_btn)
        buttons_layout.addStretch()

        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()

    # ================= LOGIKA =================

    def _save_profile(self):
        print("=== DANE LEKARZA ===")
        print("Placówka:", self.facility_input.text())
        print("Specjalizacja:", self.specialization_input.text())
        print("PWZ:", self.pwz_input.text())
        print("Miasto:", self.city_input.text())

        print("✅ Zapisano dane lekarza")

        # ⬅️ po zapisie wracamy do dashboardu
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.doctor_dashboard
        )

    def _go_back(self):
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.doctor_dashboard
        )

    # ================= STYL =================

    def _apply_style(self):
        self.setStyleSheet("""
        QWidget#doctorProfileView {
            background: transparent;
        }

        QLabel#profileHeader {
            font-size: 26px;
            font-weight: bold;
            color: white;
        }

        QLabel#profileSubHeader {
            font-size: 14px;
            color: rgba(255,255,255,0.7);
            margin-bottom: 12px;
        }

        QLineEdit#profileInput {
            background: white;
            border-radius: 18px;
            padding: 12px;
            font-size: 15px;
            color: black;
        }

        QPushButton#primaryButton {
            background: #6c63ff;
            color: white;
            border-radius: 20px;
            padding: 14px 20px;
            font-size: 15px;
            font-weight: bold;
        }

        QPushButton#primaryButton:hover {
            background: #584fff;
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
