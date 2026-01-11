"""Strona logowania użytkownika."""

from PCApp.ui.register_window import RegisterWindow

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMovie

from typing import Optional
import base64
import json


def _get_role_from_jwt(token: str) -> Optional[str]:
    """Odczyt roli z JWT bez weryfikacji podpisu (frontend only)."""
    try:
        payload_part = token.split(".")[1]
        payload_part += "=" * (-len(payload_part) % 4)
        decoded = base64.urlsafe_b64decode(payload_part)
        payload = json.loads(decoded)
        return payload.get("role")
    except Exception as e:
        print("JWT decode error:", e)
        return None


class LoginPage(QWidget):
    login_successful = pyqtSignal(dict)

    def __init__(self, strings_manager, api_client, parent=None):
        super().__init__(parent)
        self.strings = strings_manager
        self.api_client = api_client

        self.setObjectName("loginPage")
        self._setup_ui()
        self._apply_focusly_style()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_container = QWidget()
        form_container.setObjectName("loginFormContainer")
        form_container.setFixedWidth(600)

        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(60, 50, 60, 50)
        form_layout.setSpacing(20)

        title = QLabel("Focusly")
        title.setObjectName("loginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        email_label = QLabel(self.strings.get("login_email"))
        email_label.setObjectName("loginLabel")

        self.email_input = QLineEdit()
        self.email_input.setObjectName("loginInput")
        self.email_input.setPlaceholderText(
            self.strings.get("login_email_placeholder")
        )

        password_label = QLabel(self.strings.get("login_password"))
        password_label.setObjectName("loginLabel")

        self.password_input = QLineEdit()
        self.password_input.setObjectName("loginInput")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText(
            self.strings.get("login_password_placeholder")
        )
        self.password_input.returnPressed.connect(self._handle_login)

        self.login_btn = QPushButton(self.strings.get("login_button"))
        self.login_btn.setObjectName("loginButton")
        self.login_btn.clicked.connect(self._handle_login)

        self.register_btn = QPushButton("Zarejestruj się")
        self.register_btn.setObjectName("registerButton")
        self.register_btn.clicked.connect(self._open_register)

        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_movie = QMovie("PCApp/resources/animation/loading.gif")
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.hide()

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.hide()

        form_layout.addWidget(title)
        form_layout.addSpacing(30)
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(10)
        form_layout.addWidget(self.login_btn)
        form_layout.addWidget(self.register_btn)
        form_layout.addWidget(self.loading_label)
        form_layout.addWidget(self.status_label)

        main_layout.addWidget(form_container)

    # ================= LOGOWANIE =================

    def _handle_login(self):
        email = self.email_input.text().strip().lower()
        password = self.password_input.text()

        if not email or not password:
            self._show_error("Uzupełnij email i hasło")
            return

        self._set_loading(True)
        self._hide_status()

        try:
            login_response = self.api_client.login(email, password)

            access_token = None
            if isinstance(login_response, dict):
                access_token = login_response.get("access_token")

            if access_token is None:
                access_token = getattr(self.api_client, "access_token", None)

            role = _get_role_from_jwt(access_token) if access_token else None

            user_data = {
                "username": email,
                "email": email,
                "role": role
            }

            print("✅ Zalogowano (JWT):", user_data)

            self._set_loading(False)
            self.login_successful.emit(user_data)

        except Exception as e:
            print("LOGIN ERROR:", e)
            self._set_loading(False)
            self._show_error("Błędne dane logowania")

    # ================= REJESTRACJA =================

    def _open_register(self):
        self.register_window = RegisterWindow(self.api_client)
        self.register_window.show()

    # ================= UI HELPERS =================

    def _set_loading(self, loading: bool):
        for w in (
            self.login_btn,
            self.register_btn,
            self.email_input,
            self.password_input,
        ):
            w.setEnabled(not loading)

        if loading:
            self.loading_movie.start()
            self.loading_label.show()
        else:
            self.loading_movie.stop()
            self.loading_label.hide()

    def _show_error(self, message: str):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #ff4444;")
        self.status_label.show()

    def _hide_status(self):
        self.status_label.hide()

    # ================= STYL =================

    def _apply_focusly_style(self):
        """Styl Focusly dla strony logowania"""
        self.setStyleSheet("""
        QWidget#loginPage {
            background: transparent;
        }

        QLabel#loginTitle {
            font-size: 42px;
            font-weight: bold;
            color: white;
        }

        QLabel#loginLabel {
            font-size: 16px;
            color: white;
        }

        QLineEdit#loginInput {
            background-color: white;
            border-radius: 18px;
            padding: 12px;
            font-size: 15px;
            color: black;
            border: none;
        }

        QPushButton#loginButton {
            background: #6c63ff;
            color: white;
            border-radius: 22px;
            padding: 12px;
            font-size: 18px;
            font-weight: bold;
        }

        QPushButton#loginButton:hover {
            background: #584fff;
        }

        QPushButton#registerButton {
            background: transparent;
            color: #d6d3ff;
            font-size: 14px;
            border: none;
        }

        QPushButton#registerButton:hover {
            color: white;
            text-decoration: underline;
        }
        """)
