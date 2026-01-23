from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget,
    QWidget, QComboBox, QSpinBox,
    QToolButton, QScrollArea
)

from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon


class GameModeDialog(QDialog):
    """Dialog menu gry: start / ankieta / ustawienia + zapis ustawień."""

    def __init__(self, parent=None, initial_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Gra terapeutyczna - menu")
        self.setFixedSize(520, 420)
        self.setObjectName("GameDialog")

        # ustawienia (domyślne)
        self.settings = {
            "difficulty": "Średni",
            "trials": 20,
        }
        if initial_settings:
            self.settings.update(initial_settings)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        self.stack = QStackedWidget()
        self.stack.setObjectName("GameDialogStack")
        root.addWidget(self.stack)

        # strona podstawowa: menu gry
        self.menu_page = QWidget()
        self._build_menu_page()
        self.stack.addWidget(self.menu_page)

        # strona 1: ustawienia
        self.settings_page = QWidget()
        self._build_settings_page()
        self.stack.addWidget(self.settings_page)

        self.stack.setCurrentIndex(0)
        self._apply_dialog_style()

    settings_saved = pyqtSignal(dict)

    # ===================== MENU GRY =====================

    def _build_menu_page(self):
        """Buduje stronę menu: Start / Ankieta / Ustawienia."""
        layout = QVBoxLayout(self.menu_page)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QWidget()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(16, 16, 16, 16)

        layout.addWidget(card)
        layout.addStretch()

        title = QLabel("Co chcesz zrobić?")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        card_layout.addWidget(title)

        self.start_btn = QPushButton("▶ Rozpocznij grę")
        self.survey_btn = QPushButton("📝 Zrób ankietę przed")
        self.settings_btn = QPushButton("⚙ Ustawienia gry")

        card_layout.addWidget(self.start_btn)
        card_layout.addWidget(self.survey_btn)
        card_layout.addWidget(self.settings_btn)
        card_layout.addStretch()

        self.settings_btn.clicked.connect(self.show_settings_page)

    # ===================== USTAWIENIA =====================

    def _build_settings_page(self):
        """Buduje stronę ustawień: opis gry, poziom trudności, liczba prób i zapis."""
        outer = QVBoxLayout(self.settings_page)
        outer.setSpacing(12)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QWidget()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(16, 16, 16, 16)

        outer.addWidget(card)
        outer.addStretch()

        top = QHBoxLayout()
        self.back_btn = QToolButton()
        self.back_btn.setText("←")
        self.back_btn.setStyleSheet("font-size: 18px; padding: 4px 10px;")
        self.back_btn.clicked.connect(self.show_menu_page)

        top_title = QLabel("Ustawienia gry")
        top_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        top.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        top.addWidget(top_title)
        top.addStretch()
        card_layout.addLayout(top)

        # Opis zasad gry
        rules_title = QLabel("Poznaj zasady gry")
        rules_title.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(rules_title)

        # scrollowany opis zasad
        rules_scroll = QScrollArea()
        rules_scroll.setObjectName("RulesScroll")
        rules_scroll.setWidgetResizable(True)
        rules_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        rules_container = QWidget()
        rules_container.setObjectName("RulesContainer")
        rules_layout = QVBoxLayout(rules_container)
        rules_layout.setContentsMargins(0, 0, 0, 0)

        rules_label = QLabel(
            "Twoim celem jest jak naszybciej kliknąć tylko w zieloną kropkę.\n"
            "Ale uważaj! Podczas rozgrywki pojawiają się rozpraszacze, których absolutnie nie możesz kliknąć.\n"
            "Nie daj im się i skoncentruj się na właściwym celu!\n"
            "Wynik zależy od celności, czasu reakcji i liczby pomyłek.\n"
            "Poniżej możesz wybrać poziom trudności rozgrywki oraz ilość prób.\n"
            "Powodzenia!"
        )
        rules_label.setWordWrap(True)
        rules_label.setObjectName("RulesLabel")
        rules_layout.addWidget(rules_label)

        rules_scroll.setWidget(rules_container)
        rules_scroll.setFixedHeight(80)

        card_layout.addWidget(rules_scroll)

        # Poziom trudności
        diff_row = QHBoxLayout()
        diff_label = QLabel("Poziom trudności:")
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Łatwy", "Średni", "Trudny"])
        self.diff_combo.setCurrentText(self.settings.get("difficulty", "Średni"))
        diff_row.addWidget(diff_label)
        diff_row.addWidget(self.diff_combo)
        card_layout.addLayout(diff_row)

        # Liczba prób
        trials_row = QHBoxLayout()
        trials_label = QLabel("Ilość prób:")
        self.trials_spin = QSpinBox()
        self.trials_spin.setRange(10, 100)
        self.trials_spin.setValue(int(self.settings.get("trials", 20)))
        trials_row.addWidget(trials_label)
        trials_row.addWidget(self.trials_spin)
        card_layout.addLayout(trials_row)

        card_layout.addStretch()

        # Zapisz
        self.save_btn = QPushButton("💾 Zapisz")
        self.save_btn.clicked.connect(self._save_settings)
        card_layout.addWidget(self.save_btn)

        # Informacja o zapisie
        self.save_info = QLabel("")
        self.save_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.save_info.setStyleSheet("color: #00d26a; font-size: 14px;")
        card_layout.addWidget(self.save_info)

    # ============== NAWIGACJA ==================

    def show_settings_page(self):
        """Przełącza widok na ustawienia (czyści komunikat)."""
        if hasattr(self, "save_info"):
            self.save_info.setText("")
        self.stack.setCurrentIndex(1)

    def show_menu_page(self):
        """Wraca do menu."""
        self.stack.setCurrentIndex(0)

    # ================== ZAPIS ===================

    def _save_settings(self):
        """Zapisuje ustawienia lokalnie i wysyła je do MainWindow."""
        self.settings["difficulty"] = self.diff_combo.currentText()
        self.settings["trials"] = int(self.trials_spin.value())

        self.settings_saved.emit(self.settings.copy())

        self.save_info.setText("✔ Ustawienia zapisane")

    def _apply_dialog_style(self):
        self.setStyleSheet("""
        #GameDialog {
            background: qlineargradient(
                x1:0, y1:0,
                x2:1, y2:1,
                stop:0 #020024,
                stop:0.4 #090979,
                stop:1 #3f32ff
            );
            color: white;
            font-size: 14px;
        }

        QLabel {
            color: rgba(255,255,255,0.9);
        }

        /* “karta” */
        #Card {
            background: rgba(0,0,0,0.22);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 18px;
        }

        QPushButton {
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.18);
            padding: 10px 12px;
            border-radius: 14px;
            font-size: 15px;
        }
        QPushButton:hover {
            background: rgba(255,255,255,0.18);
        }
        QPushButton:pressed {
            background: rgba(255,255,255,0.10);
        }

        QToolButton {
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 12px;
            padding: 6px 10px;
            font-size: 16px;
        }
        QToolButton:hover {
            background: rgba(255,255,255,0.16);
        }

        QComboBox, QSpinBox {
            background: rgba(0,0,0,0.25);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 12px;
            padding: 6px 10px;
            min-height: 34px;
            color: white;
        }
        QComboBox::drop-down {
            border: 0px;
            width: 26px;
        }
        QComboBox QAbstractItemView {
            background: #0b0b3a;
            border: 1px solid rgba(255,255,255,0.18);
            selection-background-color: rgba(255,255,255,0.18);
            color: white;
        }
        
        #RulesScroll {
            background: transparent;
            border: 0px;
        }
        
        #RulesContainer {
            background: transparent;
        }
        
        #RulesLabel {
            font-size: 13px;
            color: rgba(255,255,255,0.82);
        }
        
        QScrollBar:vertical {
            background: transparent;
            width: 10px;
            margin: 2px 0px 2px 0px;
        }
        QScrollBar::handle:vertical {
            background: rgba(255,255,255,0.22);
            border-radius: 5px;
            min-height: 25px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(255,255,255,0.30);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: transparent;
        }

        
        
        """)