from PyQt6.QtWidgets import QApplication
import sys

# Import Twojej klasy
from ui.login_window import LoginPage

# FAKE wersje tylko do wyświetlenia UI
class DummyStrings:
    def get(self, key):
        fake = {
            "login_title": "Focusly",
            "login_email": "Adres email",
            "login_password": "Hasło",
            "login_email_placeholder": "Wpisz email",
            "login_password_placeholder": "Wpisz hasło",
            "login_button": "Zaloguj",
            "login_success": "Zalogowano!",
            "error_email_required": "Podaj email",
            "error_password_required": "Podaj hasło",
            "error_invalid_credentials": "Błędny login",
            "error_network": "Błąd sieci",
            "error_general": "Błąd"
        }
        return fake.get(key, key)


class DummyAPI:
    def login(self, email, password):
        return "fake_token"

    def get_current_user(self):
        return {"username": "test_user"}


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = LoginPage(DummyStrings(), DummyAPI())
    window.resize(1000, 700)
    window.show()

    sys.exit(app.exec())
