from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton,
    QRadioButton, QHBoxLayout,
    QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal


class RegisterWindow(QWidget):
    back_to_login = pyqtSignal()

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client

        self.setObjectName("registerPage")
        self._setup_ui()
        self._apply_style()

    # ================= UI =================
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        container.setObjectName("registerFormContainer")
        container.setFixedWidth(700)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(64, 64, 64, 56)
        layout.setSpacing(18)

        # ===== TITLE (NO BACKGROUND) =====
        title = QLabel("Focusly")
        title.setObjectName("registerTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        subtitle = QLabel("Utwórz konto")
        subtitle.setObjectName("registerSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # ===== INPUTS =====
        self.first_name = QLineEdit(placeholderText="Imię")
        self.last_name = QLineEdit(placeholderText="Nazwisko")
        self.email = QLineEdit(placeholderText="Email")

        self.password = QLineEdit(placeholderText="Hasło")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.password_repeat = QLineEdit(placeholderText="Powtórz hasło")
        self.password_repeat.setEchoMode(QLineEdit.EchoMode.Password)

        for w in (
            self.first_name, self.last_name,
            self.email, self.password, self.password_repeat
        ):
            w.setObjectName("registerInput")

        # ===== ROLE =====
        self.patient_radio = QRadioButton("Pacjent")
        self.doctor_radio = QRadioButton("Lekarz")
        self.patient_radio.setChecked(True)

        role_layout = QHBoxLayout()
        role_layout.setSpacing(36)
        role_layout.addWidget(self.patient_radio)
        role_layout.addWidget(self.doctor_radio)
        role_layout.addStretch()

        # ===== DOCTOR SELECT =====
        self.doctor_label = QLabel("Lekarz prowadzący")
        self.doctor_label.setObjectName("doctorLabel")
        self.doctor_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.doctor_combo = QComboBox()
        self.doctor_combo.setObjectName("registerInput")
        self.doctor_combo.setMaxVisibleItems(5)

        # ===== BUTTONS =====
        self.register_btn = QPushButton("Zarejestruj się")
        self.register_btn.setObjectName("registerButton")
        self.register_btn.clicked.connect(self._handle_register)

        self.back_btn = QPushButton("← Wróć do logowania")
        self.back_btn.setObjectName("backButton")
        self.back_btn.clicked.connect(self.back_to_login.emit)

        # ===== LAYOUT =====
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(16)

        layout.addWidget(self.first_name)
        layout.addWidget(self.last_name)
        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addWidget(self.password_repeat)

        layout.addSpacing(10)
        layout.addLayout(role_layout)

        layout.addWidget(self.doctor_label)
        layout.addWidget(self.doctor_combo)

        layout.addSpacing(24)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.back_btn)

        main_layout.addWidget(container)

        # ===== SIGNALS =====
        self.patient_radio.toggled.connect(self._toggle_doctor_select)
        self.doctor_radio.toggled.connect(self._toggle_doctor_select)

        self._load_doctors()
        self._toggle_doctor_select()

    # ================= LOGIC =================
    def _toggle_doctor_select(self):
        is_patient = self.patient_radio.isChecked()
        self.doctor_label.setVisible(is_patient)
        self.doctor_combo.setVisible(is_patient)

    def _load_doctors(self):
        self.doctor_combo.clear()
        self.doctor_combo.addItem("— wybierz lekarza —", None)

        try:
            doctors = self.api_client.get("/doctors")
            for d in doctors:
                name = f"{d.get('first_name','')} {d.get('last_name','')}".strip()
                self.doctor_combo.addItem(name, d["id"])
        except Exception as e:
            print("⚠️ Błąd lekarzy:", e)
            self.doctor_combo.addItem("Brak dostępnych lekarzy", None)

    def _handle_register(self):
        email = self.email.text().strip().lower()
        password = self.password.text()
        password_repeat = self.password_repeat.text()

        if not email or "@" not in email:
            print("❌ Niepoprawny email")
            return

        if not password or password != password_repeat:
            print("❌ Hasła nie są zgodne")
            return

        role = "doctor" if self.doctor_radio.isChecked() else "patient"

        payload = {
            "username": email,
            "email": email,
            "password": password,
            "role": role,
            "first_name": self.first_name.text().strip(),
            "last_name": self.last_name.text().strip()
        }

        if role == "patient":
            doctor_id = self.doctor_combo.currentData()
            if doctor_id is None:
                print("❌ Wybierz lekarza prowadzącego")
                return
            payload["doctor_id"] = doctor_id

        try:
            self.api_client.post("/register", payload)
            print("✅ Rejestracja OK")
            self.back_to_login.emit()
        except Exception as e:
            print("❌ Błąd rejestracji:", e)

    # ================= STYLE =================
    def _apply_style(self):
        self.setStyleSheet("""
        QWidget#registerPage {
            background: qlineargradient(
                x1:0, y1:0,
                x2:1, y2:1,
                stop:0 #020024,
                stop:0.4 #090979,
                stop:1 #3f32ff
            );
        }

        QWidget#registerFormContainer {
            background: rgba(8, 10, 20, 0.65);
            border-radius: 32px;
        }

        QLabel#registerTitle {
            background: transparent;
            font-size: 42px;
            font-weight: bold;
            color: white;
        }

        QLabel#registerSubtitle {
            background: transparent;
            font-size: 15px;
            color: rgba(255,255,255,0.7);
        }

        QLabel#doctorLabel {
            background: transparent;
            color: rgba(255,255,255,0.85);
            font-size: 13px;
            padding-left: 6px;
        }

        QRadioButton {
            background: transparent;
            color: white;
            font-size: 15px;
        }

        QLineEdit#registerInput,
        QComboBox#registerInput {
            background: rgba(255,255,255,0.95);
            border-radius: 22px;
            padding: 14px;
            font-size: 16px;
            color: #1a1a1a;
            border: none;
        }

        QLineEdit#registerInput:focus,
        QComboBox#registerInput:focus {
            border: 2px solid #6c63ff;
        }

        QPushButton#registerButton {
            background: #6c63ff;
            color: white;
            border-radius: 26px;
            padding: 15px;
            font-size: 17px;
            font-weight: bold;
        }

        QPushButton#registerButton:hover {
            background: #584fff;
        }

        QPushButton#backButton {
            background: transparent;
            color: #d6d3ff;
            border: none;
            font-size: 14px;
        }
        """)
