from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt
from PCApp.ui.doctor_profile_form import DoctorProfileForm


class DoctorProfileView(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)

        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # ✅ EMAIL Z JEDYNEGO ŹRÓDŁA
        email = self.main_window.current_user.get("email")

        self.form = DoctorProfileForm(email)
        self.form.profile_saved.connect(self._on_saved)

        scroll.setWidget(self.form)
        layout.addWidget(scroll)

    def _on_saved(self):
        self.main_window.show_doctor_dashboard()
