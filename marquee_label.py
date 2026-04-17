from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer, QRect, QSize
from PyQt6.QtGui import QPainter

class MarqueeLabel(QLabel):
    def __init__(self, text="", parent=None, speed=2, spacing=30):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.offset = 0
        self.speed = speed  # pixels moved per timer tick
        self.spacing = spacing  # gap between text copies

        self.pad_left = 7
        self.pad_right = 7

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(30)  # update every 30 ms


    def _text_width(self):
        return self.fontMetrics().horizontalAdvance(self.text())


    def tick(self):
        text_width = self._text_width()
        total_width = text_width + self.spacing

        if text_width <= self._content_rect().width():
            self.offset = 0  # no scroll if text fits
        else:
            self.offset = (self.offset + self.speed) % total_width

        self.update()  # force repaint


    def _content_rect(self):
        # área real usable (padding aplicado)
        return self.rect().adjusted(self.pad_left,0, -self.pad_right,0)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font())

        text = self.text()
        text_width = self._text_width()

        base = self._content_rect()
        painter.setClipRect(base) # ensures marquee text is clipped to the content area so it doesn't overflow into padding

        flags = self.alignment()

        if text_width <= base.width():
            # text fits, draw normally
            painter.drawText(base, flags, text)

        else:
            total_width = text_width + self.spacing

            x1 = base.x() - self.offset
            x2 = x1 + total_width

            r1 = QRect(x1, base.y(), text_width, base.height())
            r2 = QRect(x2, base.y(), text_width, base.height())

            painter.drawText(r1, flags, text)
            painter.drawText(r2, flags, text)


    def sizeHint(self):
        text_width = self._text_width()

        base = super().sizeHint()

        # si el texto cabe (o casi)
        if text_width <= super().sizeHint().width():
            return base + QSize(self.pad_left + self.pad_right, 0)

        # si no cabe → no forzar crecimiento
        return base