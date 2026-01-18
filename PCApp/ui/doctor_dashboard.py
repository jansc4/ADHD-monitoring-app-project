import json
import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt

from PCApp.ui.components.stat_card.stat_card import StatCard
from PCApp.ui.doctor_profile_form import DoctorProfileForm


PROFILE_PATH = "doctor_profile.json"


class DoctorDashboard(QWidget):
    def __init__(self, user_data: dict, parent=None):
        super().__init__(parent)

        self.user_data = user_data
        self.profile_completed = self._load_profile_state()

        self.setObjectName("doctorDashboard")
        self._setup_ui()
        self._apply_style()

    # ================= UI =================
    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(40, 20, 40, 24)

        email = self.user_data.get("email", "lekarzu")

        # ===== HEADER =====
        header = QLabel(f"Witaj, <span style='color:#d6d3ff'>{email}</span> 👋")
        header.setObjectName("dashboardHeader")

        subheader = QLabel("Panel lekarza")
        subheader.setObjectName("dashboardSubHeader")
        subheader.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(header)
        main_layout.addWidget(subheader)

        # ===== PROFILE FORM =====
        self.profile_container = QFrame()
        profile_layout = QVBoxLayout(self.profile_container)
        profile_layout.setContentsMargins(0, 12, 0, 12)

        email = self.user_data.get("email")
        self.profile_form = DoctorProfileForm(email)

        self.profile_form.profile_saved.connect(self._on_profile_saved)

        profile_layout.addWidget(self.profile_form)
        main_layout.addWidget(self.profile_container)

        # ===== DASHBOARD CONTENT =====
        self.dashboard_container = QFrame()
        container_layout = QVBoxLayout(self.dashboard_container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(24)
        cards_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        cards_layout.addWidget(StatCard("👥 Pacjenci", "—"))
        cards_layout.addWidget(StatCard("📊 Sesje", "—"))
        cards_layout.addWidget(StatCard("⚠️ Alerty", "—"))

        container_layout.addLayout(cards_layout)

        self.lock_info = QLabel(
            "🔒 Dostęp do pacjentów i analiz zostanie odblokowany "
            "po uzupełnieniu profilu lekarza."
        )
        self.lock_info.setObjectName("lockInfo")
        self.lock_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container_layout.addWidget(self.lock_info)

        main_layout.addWidget(self.dashboard_container)
        main_layout.addStretch(1)

        scroll.setWidget(content)
        root_layout.addWidget(scroll)

        self._update_ui_state()

    # ================= PROFILE STATE =================
    def _load_profile_state(self) -> bool:
        if not os.path.exists(PROFILE_PATH):
            return False
        try:
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data)
        except Exception:
            return False

    def _save_profile_state(self):
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(
                {"completed": True},
                f,
                ensure_ascii=False,
                indent=2
            )

    # ================= PUBLIC API =================
    def refresh(self):
        self.profile_completed = True
        self._update_ui_state()

    # ================= STATE =================
    def _on_profile_saved(self):
        self.profile_completed = True
        self._save_profile_state()
        self._update_ui_state()

    def _update_ui_state(self):
        self.profile_container.setVisible(not self.profile_completed)
        self.lock_info.setVisible(not self.profile_completed)
        self.dashboard_container.setEnabled(self.profile_completed)

    # ================= STYLE =================
    def _apply_style(self):
        self.setStyleSheet("""
        QWidget#doctorDashboard {
            background: transparent;
        }

        QLabel#dashboardHeader {
            font-size: 36px;
            font-weight: 800;
            color: white;
            margin-bottom: 2px;
        }

        QLabel#dashboardSubHeader {
            font-size: 17px;
            font-weight: 500;
            color: rgba(255,255,255,0.8);
            margin-bottom: 8px;
        }

        QLabel#lockInfo {
            font-size: 14px;
            color: rgba(255,255,255,0.65);
            margin-top: 6px;
        }
        """)
