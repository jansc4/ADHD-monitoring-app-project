"""Strona logowania użytkownika."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMovie


class LoginPage(QWidget):
    """
    Strona logowania z formularzem email/hasło.
    Komunikuje się z API poprzez api_client.
    """
    
    login_successful = pyqtSignal(dict)  # Emituje dane użytkownika po udanym logowaniu
    
    def __init__(self, strings_manager, api_client, parent=None):
        """
        Args:
            strings_manager: Menedżer tłumaczeń
            api_client: Klient API do komunikacji z backendem
            parent: Widget rodzica
        """
        super().__init__(parent)
        self.strings = strings_manager
        self.api_client = api_client
        
        self.setObjectName("loginPage")
        self._setup_ui()
        
    def _setup_ui(self):
        """Tworzy interfejs strony logowania."""
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)
        
        # Kontener formularza
        form_container = QWidget()
        form_container.setObjectName("loginFormContainer")
        form_container.setFixedWidth(400)
        
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(20)
        
        # Nagłówek
        title = QLabel(self.strings.get("login_title", "Sign In"))
        title.setObjectName("loginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.trans_key = "login_title"
        
        # Pole email
        email_label = QLabel(self.strings.get("login_email", "Email:"))
        email_label.setObjectName("loginLabel")
        email_label.trans_key = "login_email"
        
        self.email_input = QLineEdit()
        self.email_input.setObjectName("loginInput")
        self.email_input.setPlaceholderText(
            self.strings.get("login_email_placeholder", "Enter your email")
        )
        self.email_input.trans_placeholder_key = "login_email_placeholder"
        
        # Pole hasło
        password_label = QLabel(self.strings.get("login_password", "Password:"))
        password_label.setObjectName("loginLabel")
        password_label.trans_key = "login_password"
        
        self.password_input = QLineEdit()
        self.password_input.setObjectName("loginInput")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText(
            self.strings.get("login_password_placeholder", "Enter your password")
        )
        self.password_input.trans_placeholder_key = "login_password_placeholder"
        
        # Obsługa Enter
        self.password_input.returnPressed.connect(self._handle_login)
        
        # Przycisk logowania
        self.login_btn = QPushButton(self.strings.get("login_button", "Sign In"))
        self.login_btn.setObjectName("loginButton")
        self.login_btn.trans_key = "login_button"
        self.login_btn.setFixedHeight(40)
        self.login_btn.clicked.connect(self._handle_login)
        
        # Animacja ładowania (ukryta domyślnie)
        self.loading_label = QLabel()
        self.loading_label.setObjectName("loadingLabel")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_movie = QMovie("resources/animation/loading.gif")
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.hide()
        
        # Status/Error message
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        
        # Dodanie elementów do formularza
        form_layout.addWidget(title)
        form_layout.addSpacing(10)
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_btn)
        form_layout.addWidget(self.loading_label)
        form_layout.addWidget(self.status_label)
        form_layout.addStretch()
        
        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container)
        
        self.setLayout(main_layout)
    
    def _handle_login(self):
        """Obsługuje próbę logowania."""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        # Walidacja
        if not email:
            self._show_error(self.strings.get("error_email_required", "Email is required"))
            return
        
        if not password:
            self._show_error(self.strings.get("error_password_required", "Password is required"))
            return
        
        # Rozpocznij logowanie
        self._set_loading(True)
        self._hide_status()
        
        try:
            # Wywołaj API
            token = self.api_client.login(email, password)
            
            # Pobierz dane użytkownika
            user_data = self.api_client.get_current_user()
            
            # Zatrzymaj ładowanie
            self._set_loading(False)
            
            # Powiadom o sukcesie
            self.login_successful.emit(user_data)
            
            # Opcjonalnie: wyświetl sukces
            self._show_success(self.strings.get("login_success", "Login successful!"))
            
        except Exception as e:
            self._set_loading(False)
            error_msg = str(e)
            
            # Wyodrębnij bardziej czytelny komunikat błędu
            if "401" in error_msg or "Unauthorized" in error_msg:
                error_msg = self.strings.get(
                    "error_invalid_credentials", 
                    "Invalid email or password"
                )
            elif "Network" in error_msg or "Connection" in error_msg:
                error_msg = self.strings.get(
                    "error_network", 
                    "Network error. Please check your connection."
                )
            else:
                error_msg = self.strings.get(
                    "error_general", 
                    "An error occurred. Please try again."
                )
            
            self._show_error(error_msg)
    
    def _set_loading(self, loading: bool):
        """
        Włącza/wyłącza stan ładowania.
        
        Args:
            loading: True jeśli ładowanie, False w przeciwnym razie
        """
        self.login_btn.setEnabled(not loading)
        self.email_input.setEnabled(not loading)
        self.password_input.setEnabled(not loading)
        
        if loading:
            self.loading_movie.start()
            self.loading_label.show()
        else:
            self.loading_movie.stop()
            self.loading_label.hide()
    
    def _show_error(self, message: str):
        """
        Wyświetla komunikat błędu.
        
        Args:
            message: Treść komunikatu
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #ff4444;")
        self.status_label.show()
    
    def _show_success(self, message: str):
        """
        Wyświetla komunikat sukcesu.
        
        Args:
            message: Treść komunikatu
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #44ff44;")
        self.status_label.show()
    
    def _hide_status(self):
        """Ukrywa komunikat statusu."""
        self.status_label.hide()
    
    def clear_form(self):
        """Czyści formularz logowania."""
        self.email_input.clear()
        self.password_input.clear()
        self._hide_status()
    
    def rerender_theme(self):
        """Odświeża interfejs po zmianie motywu/języka."""
        # Metoda wywoływana przez główne okno przy zmianie języka/motywu
        pass
