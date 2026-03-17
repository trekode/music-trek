from PyQt6.QtWidgets import QSlider
from PyQt6.QtCore import Qt

class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Calcular la posición proporcional del clic
            new_value = self.minimum() + ((self.maximum()-self.minimum()) * event.position().x() / self.width())
            self.setValue(int(new_value))
            self.sliderMoved.emit(int(new_value))  # emitir señal para mover la canción
        super().mousePressEvent(event)
