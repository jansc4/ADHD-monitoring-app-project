"""Handler dla obsługi zmiany rozmiaru okna."""

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QWidget


class WindowResizeHandler:
    """
    Klasa obsługująca zmianę rozmiaru okna bez ramki (frameless window).
    Wykrywa pozycję kursora i umożliwia zmianę rozmiaru z każdej krawędzi/rogu.
    """
    
    MARGIN = 8  # Margines w pikselach do detekcji krawędzi
    
    def __init__(self, window: QWidget):
        """
        Args:
            window: Okno, którym ma zarządzać handler
        """
        self.window = window
        self.resizing = False
        self.resize_direction = None
        self.drag_position = QPoint()
        self.move_window = False
        self.drag_offset = QPoint()
        
    def mouse_press(self, event):
        """
        Obsługuje naciśnięcie przycisku myszy.
        
        Args:
            event: QMouseEvent
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            self.resizing = self.resize_direction is not None
            
            # Sprawdź czy naciśnięto w obszarze, który pozwala na przesuwanie okna
            # (np. belka tytułowa)
            if hasattr(self.window, 'title_bar') and \
               self.window.title_bar.underMouse() and not self.resizing:
                self.move_window = True
                self.drag_offset = event.globalPosition().toPoint() - self.window.frameGeometry().topLeft()
            else:
                self.move_window = False
    
    def mouse_move(self, event):
        """
        Obsługuje ruch myszy - zmienia kursor i wykonuje resize/move.
        
        Args:
            event: QMouseEvent
        """
        pos = event.pos()
        x, y = pos.x(), pos.y()
        w, h = self.window.width(), self.window.height()
        
        # Aktualizacja kierunku resize gdy mysz nie jest wciśnięta
        if not self.resizing and not event.buttons():
            self._update_resize_direction(x, y, w, h)
        
        # Wykonaj resize
        elif self.resizing:
            self._perform_resize(event)
        
        # Wykonaj przesunięcie okna
        elif self.move_window:
            self.window.move(event.globalPosition().toPoint() - self.drag_offset)
    
    def mouse_release(self, event):
        """
        Obsługuje zwolnienie przycisku myszy.
        
        Args:
            event: QMouseEvent
        """
        self.resizing = False
        self.move_window = False
        self.window.setCursor(Qt.CursorShape.ArrowCursor)
    
    def _update_resize_direction(self, x, y, w, h):
        """
        Aktualizuje kierunek resize na podstawie pozycji kursora.
        
        Args:
            x, y: Pozycja kursora względem okna
            w, h: Szerokość i wysokość okna
        """
        m = self.MARGIN
        
        # Sprawdź pozycję kursora i ustaw odpowiedni kierunek
        if x <= m and y <= m:
            self.resize_direction = 'topleft'
            self.window.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif x >= w - m and y <= m:
            self.resize_direction = 'topright'
            self.window.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif x <= m and y >= h - m:
            self.resize_direction = 'bottomleft'
            self.window.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif x >= w - m and y >= h - m:
            self.resize_direction = 'bottomright'
            self.window.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif x <= m:
            self.resize_direction = 'left'
            self.window.setCursor(Qt.CursorShape.SizeHorCursor)
        elif x >= w - m:
            self.resize_direction = 'right'
            self.window.setCursor(Qt.CursorShape.SizeHorCursor)
        elif y <= m:
            self.resize_direction = 'top'
            self.window.setCursor(Qt.CursorShape.SizeVerCursor)
        elif y >= h - m:
            self.resize_direction = 'bottom'
            self.window.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.resize_direction = None
            self.window.setCursor(Qt.CursorShape.ArrowCursor)
    
    def _perform_resize(self, event):
        """
        Wykonuje zmianę rozmiaru okna.
        
        Args:
            event: QMouseEvent
        """
        delta = event.globalPosition().toPoint() - self.drag_position
        geom = self.window.geometry()
        
        # Modyfikuj geometrię w zależności od kierunku
        if self.resize_direction == 'right':
            geom.setRight(geom.right() + delta.x())
        elif self.resize_direction == 'left':
            geom.setLeft(geom.left() + delta.x())
        elif self.resize_direction == 'top':
            geom.setTop(geom.top() + delta.y())
        elif self.resize_direction == 'bottom':
            geom.setBottom(geom.bottom() + delta.y())
        elif self.resize_direction == 'topright':
            geom.setTop(geom.top() + delta.y())
            geom.setRight(geom.right() + delta.x())
        elif self.resize_direction == 'topleft':
            geom.setTop(geom.top() + delta.y())
            geom.setLeft(geom.left() + delta.x())
        elif self.resize_direction == 'bottomright':
            geom.setBottom(geom.bottom() + delta.y())
            geom.setRight(geom.right() + delta.x())
        elif self.resize_direction == 'bottomleft':
            geom.setBottom(geom.bottom() + delta.y())
            geom.setLeft(geom.left() + delta.x())
        
        self.window.setGeometry(geom)
        self.drag_position = event.globalPosition().toPoint()
