"""Dialog ustawień aplikacji jako floating window."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QWidget, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal


class SettingsDialog(QDialog):
    settings_changed = pyqtSignal()
    
    def __init__(self, settings_manager, strings_manager, theme_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.strings = strings_manager
        self.theme = theme_manager
        
        self._setup_window()
        self._setup_ui()
        self._apply_style()
        
    def _setup_window(self):
        self.setWindowTitle(self.strings.get("settings_title"))
        self.setObjectName("settingsDialog")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setModal(False)
        self.setFixedSize(600, 450)
        
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.header = QLabel(self.strings.get("settings_title"))
        self.header.setObjectName("settingsHeader")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        content_layout.addWidget(self._create_language_section())
        content_layout.addWidget(self._create_separator())
        content_layout.addWidget(self._create_theme_section())
        content_layout.addWidget(self._create_separator())
        content_layout.addWidget(self._create_font_section())
        content_layout.addWidget(self._create_separator())
        content_layout.addWidget(self._create_font_size_section())
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        
        buttons_widget = QWidget()
        buttons_layout = self._create_buttons_section()
        buttons_widget.setLayout(buttons_layout)
        
        main_layout.addWidget(self.header)
        main_layout.addWidget(scroll)
        main_layout.addWidget(buttons_widget)
    
    def _create_separator(self) -> QWidget:
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: rgba(120, 120, 255, 0.3);")
        return separator
        
    def _create_language_section(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        self.lang_label = QLabel(self.strings.get("settings_language"))
        self.language_combo = QComboBox()
        self.language_combo.setMinimumHeight(35)
        
        self.language_combo.addItem("English", "lang_en")
        self.language_combo.addItem("Polski", "lang_pl")
        
        current_lang = self.settings.get("language")
        if current_lang == "en":
            current_lang = "lang_en"
        elif current_lang == "pl":
            current_lang = "lang_pl"
        
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        layout.addWidget(self.lang_label)
        layout.addWidget(self.language_combo)
        return widget
    
    def _create_theme_section(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        self.theme_label = QLabel(self.strings.get("settings_theme"))
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(35)

        self.theme_combo.addItem(self.strings.get("theme_dark"), "dark")
        self.theme_combo.addItem(self.strings.get("theme_light"), "light")
        
        current_theme = self.settings.get("theme")
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        layout.addWidget(self.theme_label)
        layout.addWidget(self.theme_combo)
        return widget
    
    def _create_font_section(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        self.font_label = QLabel(self.strings.get("settings_font"))
        self.font_combo = QComboBox()
        self.font_combo.setMinimumHeight(35)

        self.font_combo.addItem("Arial", "Arial")
        self.font_combo.addItem("Calibri", "Calibri")
        self.font_combo.addItem("Times New Roman", "NewTimesRoman")
        self.font_combo.addItem("Segoe UI", "Segoe UI")
        
        available_fonts = self.settings.get_available_values("font_family")
        for font in available_fonts:
            self.font_combo.addItem(font, font)
        
        current_font = self.settings.get("font_family")
        index = self.font_combo.findData(current_font)
        if index >= 0:
            self.font_combo.setCurrentIndex(index)
        
        layout.addWidget(self.font_label)
        layout.addWidget(self.font_combo)
        return widget
    
    def _create_font_size_section(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        self.font_size_label = QLabel(self.strings.get("settings_font_size"))
        self.font_size_combo = QComboBox()
        self.font_size_combo.setMinimumHeight(35)
        
        available_sizes = self.settings.get_available_values("font_size")
        for size in available_sizes:
            self.font_size_combo.addItem(f"{size}px", size)
        
        current_size = self.settings.get("font_size")
        index = self.font_size_combo.findData(current_size)
        if index >= 0:
            self.font_size_combo.setCurrentIndex(index)
        
        layout.addWidget(self.font_size_label)
        layout.addWidget(self.font_size_combo)
        return widget
    
    def _create_buttons_section(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)
        
        self.apply_btn = QPushButton(self.strings.get("btn_apply"))
        self.apply_btn.setMinimumHeight(40)
        self.apply_btn.clicked.connect(self._apply_settings)
        
        self.close_btn = QPushButton(self.strings.get("btn_close"))
        self.close_btn.setMinimumHeight(40)
        self.close_btn.clicked.connect(self.close)
        
        layout.addStretch()
        layout.addWidget(self.apply_btn)
        layout.addWidget(self.close_btn)
        
        return layout
    
    def _apply_settings(self):
        new_language = self.language_combo.currentData()
        new_theme = self.theme_combo.currentData()
        new_font = self.font_combo.currentData()
        new_font_size = self.font_size_combo.currentData()
        
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
        
        if changed:
            self.settings.save_settings()
            self.settings_changed.emit()
    
    def _apply_style(self):
        self.setStyleSheet("""
        QDialog#settingsDialog {
            background-color: #0f0f1a;
            color: #ffffff;
            border-radius: 14px;
        }

        QLabel {
            color: #ffffff;
            font-size: 14px;
        }

        QLabel#settingsHeader {
            font-size: 18px;
            font-weight: bold;
            padding: 14px;
            background: rgba(255,255,255,0.05);
            border-bottom: 1px solid rgba(120,120,255,0.3);
        }

        QComboBox {
            background-color: #1c1c2e;
            border: 1px solid #5a5aff;
            border-radius: 8px;
            padding: 6px 10px;
            color: #ffffff;
        }

        QComboBox::drop-down {
            border: none;
        }

        QPushButton {
            background-color: #2d2dff;
            border: none;
            border-radius: 10px;
            padding: 8px 16px;
            color: white;
        }

        QPushButton:hover {
            background-color: #4747ff;
        }
        """)
