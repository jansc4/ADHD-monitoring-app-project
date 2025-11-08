"""Dialog ustawień aplikacji jako floating window."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QWidget, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal


class SettingsDialog(QDialog):
    """
    Małe, niezależne okienko ustawień (floating dialog).
    Pozwala na zmianę języka, motywu, czcionki i rozmiaru czcionki aplikacji.
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
        self.setWindowTitle(self.strings.get("settings_title"))
        # ensure QSS rules target this widget and background/border are painted
        self.setObjectName("settingsDialog")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setModal(False)  # Pozwala na interakcję z głównym oknem
        self.setFixedSize(600, 450)  # Zwiększona wysokość dla wszystkich ustawień
        
    def _setup_ui(self):
        """Tworzy interfejs użytkownika."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Nagłówek
        self.header = QLabel(self.strings.get("settings_title"))
        self.header.setObjectName("settingsHeader")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 15px; background: rgba(0,0,0,0.2);")
        
        # Scroll area dla ustawień
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Widget z zawartością
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Sekcja języka
        lang_section = self._create_language_section()
        
        # Sekcja motywu
        theme_section = self._create_theme_section()
        
        # Sekcja czcionki
        font_section = self._create_font_section()
        
        # Sekcja rozmiaru czcionki
        font_size_section = self._create_font_size_section()
        
        # Dodanie sekcji do layoutu zawartości
        content_layout.addWidget(lang_section)
        content_layout.addWidget(self._create_separator())
        content_layout.addWidget(theme_section)
        content_layout.addWidget(self._create_separator())
        content_layout.addWidget(font_section)
        content_layout.addWidget(self._create_separator())
        content_layout.addWidget(font_size_section)
        content_layout.addStretch()
        
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        
        # Przyciski akcji
        buttons_section = self._create_buttons_section()
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_section)
        #buttons_widget.setStyleSheet("background: rgba(0,0,0,0.2); padding: 10px;")
        
        # Dodanie wszystkiego do głównego layoutu
        main_layout.addWidget(self.header)
        main_layout.addWidget(scroll)
        main_layout.addWidget(buttons_widget)
        
        self.setLayout(main_layout)
    
    def _create_separator(self) -> QWidget:
        """Tworzy separator między sekcjami."""
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: rgba(128, 128, 128, 0.3);")
        return separator
        
    def _create_language_section(self) -> QWidget:
        """Tworzy sekcję wyboru języka."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lang_label = QLabel(self.strings.get("settings_language"))
        self.lang_label.setObjectName("settingsLabel")
        #label.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("languageCombo")
        self.language_combo.setMinimumHeight(35)
        
        # Dodaj języki - używamy wartości z settings.json
        self.language_combo.addItem("English", "lang_en")
        self.language_combo.addItem("Polski", "lang_pl")
        
        # Ustaw aktualny język - normalizacja wartości
        current_lang = self.settings.get("language")
        # Konwersja starych wartości "en"/"pl" na "lang_en"/"lang_pl"
        if current_lang == "en":
            current_lang = "lang_en"
        elif current_lang == "pl":
            current_lang = "lang_pl"
        
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        layout.addWidget(self.lang_label)
        layout.addWidget(self.language_combo)
        widget.setLayout(layout)
        
        return widget
    
    def _create_theme_section(self) -> QWidget:
        """Tworzy sekcję wyboru motywu."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        self.theme_label = QLabel(self.strings.get("settings_theme"))
        self.theme_label.setObjectName("settingsLabel")
        #label.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("themeCombo")
        self.theme_combo.setMinimumHeight(35)
        self.theme_combo.addItem(
            self.strings.get("theme_dark"),
            "dark"
        )
        self.theme_combo.addItem(
            self.strings.get("theme_light"),
            "light"
        )
        
        # Ustaw aktualny motyw
        current_theme = self.settings.get("theme")
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        layout.addWidget(self.theme_label)
        layout.addWidget(self.theme_combo)
        widget.setLayout(layout)
        
        return widget
    
    def _create_font_section(self) -> QWidget:
        """Tworzy sekcję wyboru czcionki."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        self.font_label = QLabel(self.strings.get("settings_font"))
        self.font_label.setObjectName("settingsLabel")
        #label.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.font_combo = QComboBox()
        self.font_combo.setObjectName("fontCombo")
        self.font_combo.setMinimumHeight(35)
        self.font_combo.addItem("Arial", "Arial")
        self.font_combo.addItem("Calibri", "Calibri")
        self.font_combo.addItem("Times New Roman", "NewTimesRoman")
        self.font_combo.addItem("Segoe UI", "Segoe UI")
        
        # Pobierz dostępne czcionki
        available_fonts = self.settings.get_available_values("font_family")
        for font in available_fonts:
            self.font_combo.addItem(font, font)
        
        # Ustaw aktualną czcionkę
        current_font = self.settings.get("font_family")
        index = self.font_combo.findData(current_font)
        if index >= 0:
            self.font_combo.setCurrentIndex(index)
        
        layout.addWidget(self.font_label)
        layout.addWidget(self.font_combo)
        widget.setLayout(layout)
        
        return widget
    
    def _create_font_size_section(self) -> QWidget:
        """Tworzy sekcję wyboru rozmiaru czcionki."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        self.font_size_label = QLabel(self.strings.get("settings_font_size"))
        self.font_size_label.setObjectName("settingsLabel")
        #label.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.font_size_combo = QComboBox()
        self.font_size_combo.setObjectName("fontSizeCombo")
        self.font_size_combo.setMinimumHeight(35)
        
        # Pobierz dostępne rozmiary czcionek
        available_sizes = self.settings.get_available_values("font_size")
        for size in available_sizes:
            self.font_size_combo.addItem(f"{size}px", size)
        
        # Ustaw aktualny rozmiar czcionki
        current_size = self.settings.get("font_size")
        index = self.font_size_combo.findData(current_size)
        if index >= 0:
            self.font_size_combo.setCurrentIndex(index)
        
        layout.addWidget(self.font_size_label)
        layout.addWidget(self.font_size_combo)
        widget.setLayout(layout)
        
        return widget
    
    def _create_buttons_section(self) -> QHBoxLayout:
        """Tworzy sekcję przycisków akcji."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Przycisk Zastosuj
        self.apply_btn = QPushButton(self.strings.get("btn_apply"))
        self.apply_btn.setObjectName("applyBtn")
        self.apply_btn.setMinimumHeight(40)
        self.apply_btn.clicked.connect(self._apply_settings)
        
        # Przycisk Zamknij
        self.close_btn = QPushButton(self.strings.get("btn_close"))
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setMinimumHeight(40)
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
        new_font = self.font_combo.currentData()
        new_font_size = self.font_size_combo.currentData()
        
        # Sprawdź czy coś się zmieniło
        changed = False
        
        if new_language != self.settings.get("language"):
            self.settings.set("language", new_language)
            changed = True
        
        if new_theme != self.settings.get("theme"):
            self.settings.set("theme", new_theme)
            changed = True
        
        if new_font != self.settings.get("font_family"):
            self.settings.set("font_family", new_font)
            changed = True
        
        if new_font_size != self.settings.get("font_size"):
            self.settings.set("font_size", new_font_size)
            changed = True
        
        # Jeśli były zmiany, zapisz i powiadom
        if changed:
            self.settings.save_settings()
            self.settings_changed.emit()
            # self.rerender_theme()
    
    def rerender_theme(self):
        """Odświeża interfejs po zmianie motywu/języka."""
        # Zaktualizuj język w strings_manager
        current_lang = self.settings.get("language")
        self.strings.lang = current_lang.upper()
        self.strings.strings = self.strings.load_language()
        
        # Zaktualizuj tytuł okna
        self.setWindowTitle(self.strings.get("settings_title"))
        if hasattr(self, "header"):
            self.header.setText(self.strings.get("settings_title"))
        
        # Zaktualizuj wszystkie teksty
        if hasattr(self, 'apply_btn'):
            self.apply_btn.setText(self.strings.get("btn_apply"))
        if hasattr(self, 'close_btn'):
            self.close_btn.setText(self.strings.get("btn_close"))

        
        # Zaktualizuj etykiety sekcji
        # Możesz dodać więcej aktualizacji tekstów według potrzeb
        if hasattr(self, "lang_label"):
            self.lang_label.setText(self.strings.get("settings_language"))
        if hasattr(self, "theme_label"):
            self.theme_label.setText(self.strings.get("settings_theme"))
        if hasattr(self, "font_label"):
            self.font_label.setText(self.strings.get("settings_font"))
        if hasattr(self, "font_size_label"):
            self.font_size_label.setText(self.strings.get("settings_font_size"))
        
        # Zaktualizuj nazwy motywów w combobox
        if hasattr(self, 'theme_combo'):
            current_theme = self.theme_combo.currentData()
            self.theme_combo.setItemText(0, self.strings.get("theme_dark"))
            self.theme_combo.setItemText(1, self.strings.get("theme_light"))
            # Przywróć wybór
            index = self.theme_combo.findData(current_theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
