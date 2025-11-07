"""Dialog ustawień aplikacji jako floating window."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal


class SettingsDialog(QDialog):
    """
    Małe, niezależne okienko ustawień (floating dialog).
    Pozwala na zmianę języka i motywu aplikacji.
    """
    
    settings_changed = pyqtSignal()  # Sygnał emitowany po zmianie ustawień
    
    def __init__(self, settings_manager, strings_manager, theme_manager, parent=None):
        """
        Args:
            settings_manager: Menedżer ustawień
            strings_manager: Menedżer tłumaczeń
            theme_manager: Menedżer motywów
            parent: Widget rodzica
        """
        super().__init__(parent)
        self.settings = settings_manager
        self.strings = strings_manager
        self.theme = theme_manager
        
        self._setup_window()
        self._setup_ui()
        
    def _setup_window(self):
        """Konfiguruje właściwości okna."""
        self.setWindowTitle(self.strings.get("settings_title") or "Settings")
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setModal(False)  # Pozwala na interakcję z głównym oknem
        self.setFixedSize(450, 250)
        
    def _setup_ui(self):
        """Tworzy interfejs użytkownika."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Nagłówek
        header = QLabel(self.strings.get("settings_title") or "Settings")
        header.setObjectName("settingsHeader")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        
        # Sekcja języka
        lang_section = self._create_language_section()
        
        # Sekcja motywu
        theme_section = self._create_theme_section()
        
        # Przyciski akcji
        buttons_section = self._create_buttons_section()
        
        # Dodanie sekcji do layoutu
        layout.addWidget(header)
        layout.addWidget(lang_section)
        layout.addWidget(theme_section)
        layout.addStretch()
        layout.addLayout(buttons_section)
        
        self.setLayout(layout)
        
    def _create_language_section(self) -> QWidget:
        """Tworzy sekcję wyboru języka."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)

        label = QLabel(self.strings.get("settings_language") or "Language:")
        label.setObjectName("settingsLabel")
        
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("languageCombo")
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Polski", "pl")
        
        # Ustaw aktualny język
        current_lang = self.settings.get("language")
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        layout.addWidget(label)
        layout.addWidget(self.language_combo)
        widget.setLayout(layout)
        
        return widget
    
    def _create_theme_section(self) -> QWidget:
        """Tworzy sekcję wyboru motywu."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)

        label = QLabel(self.strings.get("settings_theme") or "Theme:")
        label.setObjectName("settingsLabel")
        
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("themeCombo")
        self.theme_combo.addItem(
            self.strings.get("theme_dark") or "Dark",
            "dark"
        )
        self.theme_combo.addItem(
            self.strings.get("theme_light") or "Light",
            "light"
        )
        
        # Ustaw aktualny motyw
        current_theme = self.settings.get("theme")
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        layout.addWidget(label)
        layout.addWidget(self.theme_combo)
        widget.setLayout(layout)
        
        return widget
    
    def _create_buttons_section(self) -> QHBoxLayout:
        """Tworzy sekcję przycisków akcji."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # Przycisk Zastosuj
        self.apply_btn = QPushButton(self.strings.get("btn_apply") or "Apply")
        self.apply_btn.setObjectName("applyBtn")
        self.apply_btn.clicked.connect(self._apply_settings)
        
        # Przycisk Zamknij
        self.close_btn = QPushButton(self.strings.get("btn_close") or "Close")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.clicked.connect(self.close)
        
        layout.addStretch()
        layout.addWidget(self.apply_btn)
        layout.addWidget(self.close_btn)
        
        return layout
    
    def _apply_settings(self):
        """Zapisuje i stosuje nowe ustawienia."""
        # Pobierz wybrane wartości
        new_language = self.language_combo.currentData()
        new_theme = self.theme_combo.currentData()
        
        # Sprawdź czy coś się zmieniło
        changed = False
        
        if new_language != self.settings.get("language"):
            self.settings.set("language", new_language)
            changed = True
        
        if new_theme != self.settings.get("theme"):
            self.settings.set("theme", new_theme)
            changed = True
        
        # Jeśli były zmiany, zapisz i powiadom
        if changed:
            self.settings.save_settings()
            self.settings_changed.emit()
    
    def rerender_theme(self):
        """Odświeża interfejs po zmianie motywu/języka."""
        self.setWindowTitle(self.strings.get("settings_title") or "Settings")
        
        # Aktualizuj teksty (możesz to rozszerzyć dla wszystkich elementów)
        if hasattr(self, 'apply_btn'):
            self.apply_btn.setText(self.strings.get("btn_apply") or "Apply")
        if hasattr(self, 'close_btn'):
            self.close_btn.setText(self.strings.get("btn_close") or "Close")
