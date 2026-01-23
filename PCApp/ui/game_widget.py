from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout, QToolButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

import random
import time


class ClickableField(QFrame):
    """
    Obsluga pola bez targetu w grze
    """
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class GameView(QWidget):
    """
    Widok gry badającej koncentrację użytkownika.

    Odpowiada za:
    - przebieg prób
    - logikę kliknięć
    - liczenie wyników
    - obsługę pauzy i zakończenia gry
    """
    finished = pyqtSignal(dict)
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()

        # ================= ROOT LAYOUT =================
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        # Obiektowe nazwy pod QSS
        self.setObjectName("GameView")

        # ================= TOP CARD =================
        top_bar = QWidget()
        top_bar.setObjectName("TopBar")
        top_bar.setFixedHeight(44)

        top = QHBoxLayout(top_bar)
        top.setContentsMargins(6, 2, 6, 2)
        top.setSpacing(8)

        self.back_btn = QToolButton()
        self.back_btn.setObjectName("IconBtn")
        self.back_btn.setText("←")
        self.back_btn.clicked.connect(self._request_back)

        self.difficulty_label = QLabel("Średni")
        self.difficulty_label.setObjectName("Pill")
        self.difficulty_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.pause_btn = QToolButton()
        self.pause_btn.setObjectName("IconBtn")
        self.pause_btn.setText("⏸")
        self.pause_btn.clicked.connect(self.toggle_pause)

        top.addWidget(self.back_btn)
        top.addStretch()
        top.addWidget(self.difficulty_label)
        top.addSpacing(10)
        top.addWidget(self.pause_btn)

        root.addWidget(top_bar)

        # ================= MAIN CARD =================
        main_card = QWidget()
        main_card.setObjectName("Card")
        main_layout = QVBoxLayout(main_card)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        self.info_label = QLabel("Klikaj w kropkę jak najszybciej\nI nie daj się rozproszyć")
        self.info_label.setObjectName("GameTitle")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Plansza gry
        self.field = ClickableField()
        self.field.setObjectName("GameField")
        self.field.setFixedSize(600, 420)
        self.field.clicked.connect(self._on_field_click)

        # Status/feedback na dole (TARGET / MISS / WRONG)
        self.feedback_label = QLabel("")
        self.feedback_label.setObjectName("GameFeedback")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.info_label)
        main_layout.addWidget(self.field, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.feedback_label)

        root.addWidget(main_card)

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

        # Lista distractorów
        self.distractors = []
        self.max_distractors_per_trial = 1

        for _ in range(6):  # maksymalnie 6 dla trudnego
            d = QPushButton("", self.field)
            d.setFixedSize(44, 44)
            d.setStyleSheet("""
                        QPushButton {
                            background: #ff3b3b;
                            border-radius: 22px;
                        }
                    """)
            d.clicked.connect(self._on_distractor_click)
            d.hide()
            self.distractors.append(d)

        # Timery
        self.trial_timeout_timer = QTimer(self)
        self.trial_timeout_timer.setSingleShot(True)
        self.trial_timeout_timer.timeout.connect(self._on_trial_timeout)

        self.iti_timer = QTimer(self)  # przerwa między próbami
        self.iti_timer.setSingleShot(True)
        self.iti_timer.timeout.connect(self._start_trial)

        # Stan gry
        self.max_trials = 20
        self.trial_time_limit_ms = 1200  # ile ma czasu na klikniecie
        self.iti_ms = 350  # przerwa po próbie
        self.trial_index = 0
        self.waiting_for_click = False
        self.trial_start_ts = None
        self.difficulty = "Średni"
        self.no_target_rate = 0.2  # 20% prób bez targetu
        self.current_trial_has_target = True

        self.results = []  # lista słowników: rt/miss/distractor itp.

        self.is_running = False
        self.is_paused = False
        self._remaining_ms = None
        self._elapsed_before_pause_ms = 0.0

        # żeby poprawnie wznawiać bodźce po pauzie
        self._paused_dot_was_visible = False
        self._paused_visible_distractors = []

        # stan wyglądu planszy (ciemne tło między próbami / w pauzie)
        self.field.setProperty("dimmed", False)

        # Zastosuj styl
        self._apply_game_style()

        # Ustaw początkowy feedback neutralny
        self._set_feedback("", "neutral")

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
        for d in self.distractors:
            d.hide()
        self.is_running = True
        self.is_paused = False
        self._remaining_ms = None
        self._elapsed_before_pause_ms = 0.0
        self.pause_btn.setText("⏸")

        self.info_label.setText("Start! Klikaj tylko w zieloną kropkę.")
        self.iti_timer.start(300)
        self._set_field_dimmed(False)
        self._set_feedback("", "neutral")

    # -------- POZIOMY TRUDNOŚCi --------

    def set_difficulty(self, difficulty: str):
        """Ustawia poziom trudności i parametry rozgrywki."""
        self.difficulty = difficulty
        self.difficulty_label.setText(difficulty)

        if difficulty == "Łatwy":
            self.max_distractors_per_trial = 1
            self.no_target_rate = 0.10
        elif difficulty == "Średni":
            self.max_distractors_per_trial = 3
            self.no_target_rate = 0.20
        elif difficulty == "Trudny":
            self.max_distractors_per_trial = 6
            self.no_target_rate = 0.30

    # ---------- LOGIKA TRIALI ----------
    def _start_trial(self):
        """Rozpoczyna nową próbę: losuje target i distraktory."""
        self.trial_index += 1
        if self.trial_index > self.max_trials:
            self._finish()
            return

        progress = self.trial_index / self.max_trials
        max_for_now = max(1, int(self.max_distractors_per_trial * progress))
        num_distractors = random.randint(0, max_for_now)

        self._set_field_dimmed(False)
        self._set_feedback("", "neutral")

        # losuj czy w tej próbie jest target
        self.current_trial_has_target = (random.random() >= self.no_target_rate)

        # Target pojawia się tylko w części prób (no-target = brak zielonego)
        self.dot.hide()
        if self.current_trial_has_target:
            self._move_button_randomly(self.dot, avoid_rects=[])
            self.dot.show()

        # Ustaw distraktor w innym miejscu
        for d in self.distractors:
            d.hide()

        if num_distractors > 0:
            used_rects = []
            if self.current_trial_has_target and self.dot.isVisible():
                used_rects.append(self.dot.geometry())

            for i in range(num_distractors):
                d = self.distractors[i]
                self._move_button_randomly(d, avoid_rects=used_rects)
                used_rects.append(d.geometry())
                d.show()

        # Start pomiaru
        self.waiting_for_click = True
        self.trial_start_ts = time.time()

        self.trial_timeout_timer.start(self.trial_time_limit_ms)

        self.info_label.setText(f"Próba {self.trial_index}/{self.max_trials}")

    def _on_target_click(self):
        """Obsługuje kliknięcie w target."""
        if not self.waiting_for_click:
            return

        if not self.current_trial_has_target:
            self._end_trial("false_alarm", None)
            return

        rt = (time.time() - self.trial_start_ts) * 1000
        self._end_trial("hit", rt)

    def _on_field_click(self):
        """Obsługa kliknięcia w tło planszy."""
        if not self.waiting_for_click:
            return

        # w no-target: każdy klik = false alarm
        if not self.current_trial_has_target:
            rt = None
            if self.trial_start_ts is not None:
                rt = (time.time() - self.trial_start_ts) * 1000
            self._end_trial("false_alarm", rt)
            return

        # w target trial ignoruje klik w tło
        return

    def _on_distractor_click(self):
        """Obsługa kliknięcia w distraktor."""
        if not self.waiting_for_click:
            return

        rt = (time.time() - self.trial_start_ts) * 1000
        event = "distractor_click" if self.current_trial_has_target else "false_alarm"
        self._end_trial(event, rt)

    def _on_trial_timeout(self):
        """Reakcja na brak odpowiedzi w określonym czasie."""

        if not self.waiting_for_click:
            return

        if self.current_trial_has_target:
            self._end_trial("miss", None)
        else:
            self._end_trial("no_target_ok", None)

    def _end_trial(self, event, rt_ms):
        """Kończy próbę i zapisuje wynik."""
        self.waiting_for_click = False
        self.trial_timeout_timer.stop()
        if event == "hit":
            self._set_feedback("TARGET", "good")
        elif event == "miss":
            self._set_feedback("MISS", "bad")
        elif event in ("distractor_click", "false_alarm"):
            self._set_feedback("WRONG", "bad")
        elif event == "no_target_ok":
            self._set_feedback("OK", "good")
        else:
            self._set_feedback("", "neutral")

        self.dot.hide()
        for d in self.distractors:
            d.hide()

        self._set_field_dimmed(True)

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
        false_alarms = sum(1 for r in self.results if r["event"] == "false_alarm")
        no_target_ok = sum(1 for r in self.results if r["event"] == "no_target_ok")

        mean_rt = None
        if hits:
            mean_rt = sum(r["rt_ms"] for r in hits if r["rt_ms"] is not None) / len(hits)

        accuracy = len(hits) / len(self.results) if self.results else 0

        focus_score = max(0, min(100, int(
            100 * accuracy - 10 * distractor_clicks - 5 * misses - 12 * false_alarms
        )))

        result = {
            "trials": len(self.results),
            "hits": len(hits),
            "misses": misses,
            "distractor_clicks": distractor_clicks,
            "false_alarms": false_alarms,
            "no_target_ok": no_target_ok,
            "accuracy": accuracy,
            "mean_rt_ms": mean_rt,
            "focus_score": focus_score
        }

        self.info_label.setText("Koniec sesji")
        self.is_running = False
        self.is_paused = False
        self._set_field_dimmed(True)

        self.finished.emit(result)

    # Obsługa pauz i wznowienia gry

    def _request_back(self):
        """Żądanie opuszczenia gry (emitowany sygnał)."""
        self.back_requested.emit()

    def toggle_pause(self):
        """Przełącza stan pauzy gry."""
        if not self.is_running:
            return
        if self.is_paused:
            self.resume_game()
        else:
            self.pause_game()

    def pause_game(self):
        """Pauza gry i zatrzymanie timerów"""
        if self.is_paused or not self.is_running:
            return

        self.is_paused = True
        self.pause_btn.setText("▶")

        # zatrzymaj timery
        if self.trial_timeout_timer.isActive():
            self.trial_timeout_timer.stop()

        if self.iti_timer.isActive():
            self.iti_timer.stop()

        # jeśli pauza w trakcie próby, liczy ile zostało czasu
        if self.waiting_for_click and self.trial_start_ts is not None:
            elapsed_ms = (time.time() - self.trial_start_ts) * 1000.0
            self._elapsed_before_pause_ms = elapsed_ms
            self._remaining_ms = max(0, int(self.trial_time_limit_ms - elapsed_ms))
        else:
            self._remaining_ms = None
            self._elapsed_before_pause_ms = 0.0

        # zapamietanie widoku
        self._paused_dot_was_visible = self.dot.isVisible()
        self._paused_visible_distractors = [d.isVisible() for d in self.distractors]

        # ukrywanie kropek w pauzie
        self.dot.hide()
        for d in self.distractors:
            d.hide()
        self._set_field_dimmed(True)
        self._set_feedback("", "neutral")
        self.info_label.setText("Pauza")

    def resume_game(self):
        """Wznowienie gry."""
        if not self.is_paused or not self.is_running:
            return

        self.is_paused = False
        self.pause_btn.setText("⏸")

        # jeśli pauza w trakcie próby
        if self.waiting_for_click and self._remaining_ms is not None:
            self.trial_start_ts = time.time() - (self._elapsed_before_pause_ms / 1000.0)
            self._set_field_dimmed(False)

            if self._paused_dot_was_visible:
                self.dot.show()

            for d, was_visible in zip(self.distractors, self._paused_visible_distractors):
                if was_visible:
                    d.show()

            self.trial_timeout_timer.start(self._remaining_ms)
            self.info_label.setText(f"Próba {self.trial_index}/{self.max_trials}")
        else:
            # jeśli pauza między próbami
            self.iti_timer.start(self.iti_ms)
            self.info_label.setText(f"Próba {self.trial_index}/{self.max_trials}")

    def abort_game(self):
        """Przerwanie gry bez zapisu wyniku"""
        self.trial_timeout_timer.stop()
        self.iti_timer.stop()
        self.dot.hide()
        for d in self.distractors:
            d.hide()

        self.waiting_for_click = False
        self.is_running = False
        self.is_paused = False
        self._set_field_dimmed(True)
        self.info_label.setText("Sesja przerwana")
        self._set_feedback("", "neutral")

    # ---------- HELPERY ----------

    def _move_button_randomly(self, btn: QPushButton, avoid_rects=None, padding: int = 6):
        """
        Losuje pozycję targetu tak, aby nie kolidował z innymi bodżcami
        """
        w = self.field.width()
        h = self.field.height()
        bw = btn.width()
        bh = btn.height()

        if avoid_rects is None:
            avoid_rects = []

        expanded = []
        for r in avoid_rects:
            rr = r.adjusted(-padding, -padding, padding, padding)
            expanded.append(rr)

        for _ in range(120):  # więcej prób dla 6 distractorów
            x = random.randint(0, max(0, w - bw))
            y = random.randint(0, max(0, h - bh))

            rect = btn.geometry()
            rect.moveTo(x, y)

            if all(not rect.intersects(r) for r in expanded):
                btn.move(x, y)
                return

        # fallback: jak się nie udało, ustaw w rogu
        btn.move(0, 0)

    def _apply_game_style(self):
        self.setStyleSheet("""
        #GameView {
            background: transparent;
        }

        #Card {
            background: rgba(0,0,0,0.22);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 18px;
        }

        #GameTitle {
            font-size: 20px;
            font-weight: 700;
            color: rgba(255,255,255,0.92);
        }

        #GameFeedback {
            font-size: 16px;
            font-weight: 800;
            letter-spacing: 1px;
            padding: 6px 0px;
            color: rgba(255,255,255,0.85);
        }

        #Pill {
            background: rgba(0,0,0,0.25);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 12px;
            padding: 4px 10px;
            font-size: 13px;
            color: rgba(255,255,255,0.9);
        }

        #IconBtn {
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 12px;
            padding: 6px 10px;
            font-size: 16px;
        }
        #IconBtn:hover {
            background: rgba(255,255,255,0.16);
        }

        #GameField {
            background: rgba(0,0,0,0.20);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 18px;
        }

        /* tryb "ściemniony" między próbami i w pauzie */
        #GameField[dimmed="true"] {
            background: rgba(0,0,0,0.85);
            border: 1px solid rgba(255,255,255,0.08);
        }
        
        #TopBar {
            background: rgba(0,0,0,0.15);
            border-radius: 12px;
        }

        """)

    def _set_feedback(self, text: str, kind: str):
        self.feedback_label.setText(text)
        if kind == "good":
            self.feedback_label.setStyleSheet(
                "font-size:16px; font-weight:800; letter-spacing:1px; color: rgba(0,210,106,0.95); padding: 6px 0px;"
            )
        elif kind == "bad":
            self.feedback_label.setStyleSheet(
                "font-size:16px; font-weight:800; letter-spacing:1px; color: rgba(255,59,59,0.95); padding: 6px 0px;"
            )
        else:
            self.feedback_label.setStyleSheet(
                "font-size:16px; font-weight:800; letter-spacing:1px; color: rgba(255,255,255,0.85); padding: 6px 0px;"
            )

    def _set_field_dimmed(self, dimmed: bool):
        """Przyciemnianie planszy."""
        self.field.setProperty("dimmed", dimmed)
        self.field.style().unpolish(self.field)
        self.field.style().polish(self.field)
        self.field.update()
