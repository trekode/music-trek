from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QWidget


class FloatingVolumePanel(QWidget):
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("floating_volume_panel")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 200))
        painter.drawRoundedRect(self.rect(), 10, 10)


    def hideEvent(self, event):
        self.closed.emit()
        super().hideEvent(event)