from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt


class Sidebar(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        self.setFixedWidth(220)
        self.setObjectName("sidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Focusly")
        title.setObjectName("sidebarTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addSpacing(20)

        def btn(text, handler):
            b = QPushButton(text)
            b.setObjectName("sidebarButton")
            b.clicked.connect(handler)
            layout.addWidget(b)

        btn("🏠 Dashboard", self.main_window.show_doctor_dashboard)
        btn("👤 Mój profil", self.main_window.show_doctor_profile)
        btn("👥 Moi pacjenci", self.main_window.show_patients)
        btn("📅 Kalendarz", self.main_window.show_calendar)
        btn("⚙️ Ustawienia", self.main_window.show_settings)
        btn("🚪 Wyloguj", self.main_window.logout)

        layout.addStretch()

        self.setStyleSheet("""
        QWidget#sidebar {
            background: rgba(0,0,0,0.35);
        }
        QLabel#sidebarTitle {
            color: white;
            font-size: 22px;
            font-weight: bold;
        }
        QPushButton#sidebarButton {
            background: transparent;
            color: white;
            border: none;
            text-align: left;
            padding: 12px;
            font-size: 15px;
            border-radius: 10px;
        }
        QPushButton#sidebarButton:hover {
            background: rgba(255,255,255,0.15);
        }
        """)
