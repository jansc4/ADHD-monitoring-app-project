from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class StatCard(QWidget):
    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent)

        # 🔥 TO JEST KLUCZ
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setObjectName("statCard")
        self.setFixedSize(260, 140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("statCardTitle")

        value_label = QLabel(value)
        value_label.setObjectName("statCardValue")

        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(value_label)

        self.setStyleSheet("""
        QWidget#statCard {
            background-color: rgba(108, 99, 255, 0.10);
            border: 2px solid #6c63ff;
            border-radius: 18px;
        }

        QLabel#statCardTitle {
            color: white;
            font-size: 15px;
            font-weight: 500;
        }

        QLabel#statCardValue {
            color: white;
            font-size: 22px;
            font-weight: bold;
        }
        """)
