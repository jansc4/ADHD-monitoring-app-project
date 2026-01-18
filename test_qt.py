import sys
from PyQt6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
label = QLabel("QT DZIAŁA")
label.resize(200, 100)
label.show()
sys.exit(app.exec())

