from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtCore import Qt

class GlowLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.glow_enabled = False
        self.text_color = QColor("#FFFFFF")
        self.glow_color = QColor(56, 0, 145, 50)

    def highlight(self, enabled: bool, color: QColor, background: QColor):
        self.glow_enabled = enabled
        self.text_color = color

    def setGlowEnabled(self, enabled: bool):
        self.glow_enabled = enabled
        self.update()

    def setTextColor(self, color: QColor):
        self.text_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font())

        rect = self.rect()
        text = self.text()

        # painter.fillRect(rect, self.background_color)

        if self.glow_enabled:
            painter.setPen(self.glow_color)
            for dx in (-2, -1, 0, 1, 2):
                for dy in (-2, -1, 0, 1, 2):
                    painter.drawText(
                        rect.translated(dx, dy),
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        text
                    )

        painter.setPen(self.text_color)
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            text
        )