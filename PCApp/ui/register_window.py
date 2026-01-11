from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton,
    QRadioButton, QHBoxLayout
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

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        container.setObjectName("registerFormContainer")
        container.setFixedWidth(720)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(70, 80, 70, 60)  # 🔧 WIĘCEJ GÓRY
        layout.setSpacing(18)

        # ===== TYTUŁ =====
        title = QLabel("Focusly")
        title.setObjectName("registerTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ===== POLA =====
        self.first_name = QLineEdit(placeholderText="Imię")
        self.last_name = QLineEdit(placeholderText="Nazwisko")
        self.age = QLineEdit(placeholderText="Wiek")
        self.address = QLineEdit(placeholderText="Adres")
        self.email = QLineEdit(placeholderText="Email")

        self.password = QLineEdit(placeholderText="Hasło")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.password_repeat = QLineEdit(placeholderText="Powtórz hasło")
        self.password_repeat.setEchoMode(QLineEdit.EchoMode.Password)

        for w in [
            self.first_name, self.last_name, self.age,
            self.address, self.email,
            self.password, self.password_repeat
        ]:
            w.setObjectName("registerInput")

        # ===== TYP KONTA =====
    

        self.patient_radio = QRadioButton("Pacjent")
        self.doctor_radio = QRadioButton("Lekarz")
        self.patient_radio.setChecked(True)

        role_layout = QHBoxLayout()
        role_layout.setSpacing(40)
        role_layout.addWidget(self.patient_radio)
        role_layout.addWidget(self.doctor_radio)
        role_layout.addStretch()

        # ===== PRZYCISKI =====
        self.register_btn = QPushButton("Zarejestruj się")
        self.register_btn.setObjectName("registerButton")
        self.register_btn.clicked.connect(self._handle_register)

        self.back_btn = QPushButton("← Wróć do logowania")
        self.back_btn.setObjectName("backButton")
        self.back_btn.clicked.connect(self.back_to_login.emit)

        # ===== UKŁAD =====
        layout.addWidget(title)
        layout.addSpacing(10)

        layout.addWidget(self.first_name)
        layout.addWidget(self.last_name)
        layout.addWidget(self.age)
        layout.addWidget(self.address)
        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addWidget(self.password_repeat)

        layout.addSpacing(12)
        layout.addLayout(role_layout)

        layout.addSpacing(24)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.back_btn)

        main_layout.addWidget(container)

    def _handle_register(self):
        email = self.email.text().strip()
        password = self.password.text()
        password_repeat = self.password_repeat.text()

        if not email or "@" not in email:
            print("Niepoprawny email")
            return

        if not password or password != password_repeat:
            print("Błąd hasła")
            return

        role = "doctor" if self.doctor_radio.isChecked() else "patient"

        payload = {
            "username": email,
            "email": email,
            "password": password,
            "role": role
        }

        try:
            self.api_client.post("/register", payload)
            self.back_to_login.emit()
        except Exception as e:
            print("Błąd rejestracji:", e)

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
            background-color: rgba(0, 0, 0, 0.45);
            border-radius: 28px;
        }

        QLabel#registerTitle {
            background: transparent;
            font-size: 42px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        }

       

        QRadioButton {
            background: transparent;
            color: white;
            font-size: 15px;
        }

        QRadioButton::indicator {
            width: 16px;
            height: 16px;
        }

        QLineEdit#registerInput {
            background: white;
            border-radius: 22px;
            padding: 14px;
            font-size: 16px;
            color: black;
            border: none;
        }

        QLineEdit#registerInput:focus {
            border: 2px solid #6c63ff;
        }

        QPushButton#registerButton {
            background: #6c63ff;
            color: white;
            border-radius: 24px;
            padding: 14px;
            font-size: 18px;
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
