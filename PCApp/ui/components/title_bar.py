"""Niestandardowa belka tytułowa z przyciskami sterującymi."""

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QSize, pyqtSignal


class TitleBar(QWidget):
    """
    Niestandardowa belka tytułowa z przyciskami sterującymi oknem.
    
    Sygnały:
        close_clicked: Zamknięcie aplikacji
        minimize_clicked: Minimalizacja okna
        maximize_clicked: Maksymalizacja/przywrócenie okna
        fullscreen_clicked: Pełny ekran
        settings_clicked: Otwarcie ustawień
    """
    
    close_clicked = pyqtSignal()
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    fullscreen_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    
    def __init__(self, theme_manager, strings_manager, parent=None):
        """
        Args:
            theme_manager: Menedżer motywów
            strings_manager: Menedżer tłumaczeń
            parent: Widget rodzica
        """
        super().__init__(parent)
        self.theme = theme_manager
        self.strings = strings_manager
        
        self.setObjectName("titleBar")
        self.setFixedHeight(40)
        self.setMouseTracking(True)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Tworzy interfejs belki tytułowej."""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        
        # Przycisk ustawień po lewej stronie
        self.btn_settings = self._create_button(
            name="settingsTitleBtn",
            size=30,
            icon_path="PCApp/resources/icons/alt-cog-svgrepo-com.svg",
            icon_size=24,
            callback=self.settings_clicked.emit,
            tooltip=self.strings.get("btn_settings")
        )
        self.btn_settings.trans_tooltip_key = "btn_settings"
        
        # Tytuł aplikacji
        self.title_label = QLabel(self.strings.get("app_title"), objectName="titleLabel")
        self.title_label.trans_key = "app_title"
        self.title_label.setFixedHeight(38)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        # Przyciski kontroli okna po prawej stronie
        self.btn_fullscreen = self._create_button(
            name="fullBtn",
            size=30,
            icon_path="PCApp/resources/icons/alt-expand-svgrepo-com.svg",
            icon_size=24,
            callback=self.fullscreen_clicked.emit,
            tooltip=self.strings.get("btn_full")
        )
        self.btn_fullscreen.trans_tooltip_key = "btn_full"
        
        self.btn_minimize = self._create_button(
            name="minBtn",
            size=30,
            icon_path="PCApp/resources/icons/alt-minus-window-svgrepo-com.svg",
            icon_size=24,
            callback=self.minimize_clicked.emit,
            tooltip=self.strings.get("btn_min")
        )
        self.btn_minimize.trans_tooltip_key = "btn_min"
        
        self.btn_maximize = self._create_button(
            name="maxBtn",
            size=30,
            icon_path="PCApp/resources/icons/plus-window-svgrepo-com.svg",
            icon_size=24,
            callback=self.maximize_clicked.emit,
            tooltip=self.strings.get("btn_max")
        )
        self.btn_maximize.trans_tooltip_key = "btn_max"
        
        self.btn_close = self._create_button(
            name="closeBtn",
            size=30,
            icon_path="PCApp/resources/icons/standby-svgrepo-com.svg",
            icon_size=24,
            callback=self.close_clicked.emit,
            tooltip=self.strings.get("action_quit")
        )
        self.btn_close.trans_tooltip_key = "action_quit"
        
        # Układanie elementów
        layout.addWidget(self.btn_settings)
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.btn_fullscreen)
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_maximize)
        layout.addWidget(self.btn_close)
        
        self.setLayout(layout)
    
    def _create_button(self, name, size, icon_size, icon_path, callback, tooltip=""):
        """
        Tworzy przycisk z ikoną i konfiguracją.
        
        Args:
            name: Nazwa obiektu (objectName)
            size: Rozmiar przycisku (int lub tuple)
            icon_size: Rozmiar ikony
            icon_path: Ścieżka do pliku SVG
            callback: Funkcja wywoływana po kliknięciu
            tooltip: Tekst podpowiedzi
            
        Returns:
            QPushButton: Skonfigurowany przycisk
        """
        btn = QPushButton()
        btn.setObjectName(name)
        
        if isinstance(size, int):
            btn.setFixedSize(size, size)
        else:
            btn.setFixedSize(size)
        
        icon = self.theme.colored_svg_icon(path=icon_path, color_key="icons", size=icon_size)
        btn.setIcon(icon)
        btn.setIconSize(QSize(icon_size, icon_size))
        btn.setToolTip(tooltip)
        btn.clicked.connect(callback)
        
        # Lambda do odświeżania ikony po zmianie motywu
        btn.rerender_theme = lambda: btn.setIcon(
            self.theme.colored_svg_icon(path=icon_path, color_key="icons", size=icon_size)
        )
        
        return btn
    
    def rerender_theme(self):
        """Odświeża wszystkie elementy po zmianie motywu."""
        for btn in [self.btn_settings, self.btn_fullscreen, self.btn_minimize, 
                    self.btn_maximize, self.btn_close]:
            if hasattr(btn, 'rerender_theme'):
                btn.rerender_theme()
