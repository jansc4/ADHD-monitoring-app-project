from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import random
import time


class GameView(QWidget):
    """
    Widok gry badającej koncentrację pacjenta.

    Emisja sygnału finished po zakończeniu sesji
    z wynikiem w postaci słownika.
    """
    finished = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)
        root.setSpacing(16)

        self.info_label = QLabel("Klikaj w kropkę jak najszybciej.")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 20px; color: white;")

        # Plansza gry
        self.field = QFrame()
        self.field.setFixedSize(600, 420)
        self.field.setStyleSheet("background: rgba(0,0,0,0.25); border-radius: 18px;")

        root.addWidget(self.info_label)
        root.addWidget(self.field, alignment=Qt.AlignmentFlag.AlignCenter)

        # KROPKA (target)
        self.dot = QPushButton("", self.field)
        self.dot.setFixedSize(44, 44)
        self.dot.setStyleSheet("""
            QPushButton {
                background: #00d26a;
                border-radius: 22px;
            }
            QPushButton:hover {
                background: #00b85c;
            }
        """)
        self.dot.clicked.connect(self._on_target_click)
        self.dot.hide()

        # Distraktor (po kilku próbach)
        self.distractor = QPushButton("", self.field)
        self.distractor.setFixedSize(44, 44)
        self.distractor.setStyleSheet("""
            QPushButton {
                background: #ff3b3b;
                border-radius: 22px;
            }
        """)
        self.distractor.clicked.connect(self._on_distractor_click)
        self.distractor.hide()

        # Timery
        self.trial_timeout_timer = QTimer(self)
        self.trial_timeout_timer.setSingleShot(True)
        self.trial_timeout_timer.timeout.connect(self._on_trial_timeout)

        self.iti_timer = QTimer(self)  # przerwa między próbami
        self.iti_timer.setSingleShot(True)
        self.iti_timer.timeout.connect(self._start_trial)

        # Stan gry
        self.max_trials = 20
        self.trial_time_limit_ms = 1200  # ile ma czasu na klik
        self.iti_ms = 350  # przerwa po próbie
        self.trial_index = 0
        self.waiting_for_click = False
        self.trial_start_ts = None

        self.results = []  # lista słowników: rt/miss/distractor itp.

    # ---------- PUBLICZNE API ----------
    def start_game(self):
        """
        Resetuje grę i rozpoczyna nową sesję.
        Wywoływana z MainWindow po kliknięciu przycisku.
        """
        self.trial_timeout_timer.stop()
        self.iti_timer.stop()
        self.trial_index = 0
        self.results = []
        self.waiting_for_click = False
        self.trial_start_ts = None
        self.dot.hide()
        self.distractor.hide()

        self.info_label.setText("Start! Klikaj w zieloną kropkę.")
        self.iti_timer.start(300)  # krótki start

    # ---------- LOGIKA TRIALI ----------
    def _start_trial(self):
        self.trial_index += 1
        if self.trial_index > self.max_trials:
            self._finish()
            return

        # UTRUDNIENIA: po 6 próbach distraktor
        use_distractor = self.trial_index >= 7

        # Ustaw losową pozycję targetu
        self._move_button_randomly(self.dot)
        self.dot.show()

        # Ustaw distraktor w innym miejscu
        if use_distractor:
            self._move_button_randomly(self.distractor, avoid_rect=self.dot.geometry())
            self.distractor.show()
        else:
            self.distractor.hide()

        # Start pomiaru
        self.waiting_for_click = True
        self.trial_start_ts = time.time()

        self.trial_timeout_timer.start(self.trial_time_limit_ms)

        self.info_label.setText(f"Próba {self.trial_index}/{self.max_trials}")

    def _on_target_click(self):
        """Obsługa kliknięcia w target."""
        if not self.waiting_for_click:
            return

        rt = (time.time() - self.trial_start_ts) * 1000
        self._end_trial("hit", rt)

    def _on_distractor_click(self):
        """Obsługa kliknięcia w distraktor."""
        if not self.waiting_for_click:
            return

        rt = (time.time() - self.trial_start_ts) * 1000
        self._end_trial("distractor_click", rt)

    def _on_trial_timeout(self):
        """Obsługa braku reakcji."""
        if not self.waiting_for_click:
            return

        self._end_trial("miss", None)

    def _end_trial(self, event, rt_ms):
        """Kończy próbę i zapisuje wynik."""
        self.waiting_for_click = False
        self.trial_timeout_timer.stop()

        self.dot.hide()
        self.distractor.hide()

        self.results.append({
            "trial": self.trial_index,
            "event": event,
            "rt_ms": rt_ms
        })

        self.iti_timer.start(self.iti_ms)

    def _finish(self):
        """Oblicza statystyki i emituje wynik gry."""
        hits = [r for r in self.results if r["event"] == "hit"]
        misses = sum(1 for r in self.results if r["event"] == "miss")
        distractor_clicks = sum(1 for r in self.results if r["event"] == "distractor_click")

        mean_rt = None
        if hits:
            mean_rt = sum(r["rt_ms"] for r in hits if r["rt_ms"] is not None) / len(hits)

        accuracy = len(hits) / len(self.results) if self.results else 0

        focus_score = max(0, min(100, int(
            100 * accuracy - 10 * distractor_clicks - 5 * misses
        )))

        result = {
            "trials": len(self.results),
            "hits": len(hits),
            "misses": misses,
            "distractor_clicks": distractor_clicks,
            "accuracy": accuracy,
            "mean_rt_ms": mean_rt,
            "focus_score": focus_score
        }

        self.info_label.setText("Koniec sesji")
        self.finished.emit(result)

    # ---------- HELPERY ----------
    def _move_button_randomly(self, btn: QPushButton, avoid_rect=None):
        w = self.field.width()
        h = self.field.height()
        bw = btn.width()
        bh = btn.height()

        # próby losowania pozycji
        for _ in range(50):
            x = random.randint(0, max(0, w - bw))
            y = random.randint(0, max(0, h - bh))
            rect = btn.geometry()
            rect.moveTo(x, y)
            if avoid_rect is None or not rect.intersects(avoid_rect):
                btn.move(x, y)
                return

        # fallback
        btn.move(0, 0)
