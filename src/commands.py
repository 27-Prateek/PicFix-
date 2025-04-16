# src/commands.py
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QLabel, QRubberBand
from PyQt5.QtCore import QRect, QSize
from PyQt5.QtGui import QImage, QPixmap, QTransform

class Command(ABC):
    """Abstract base class for commands."""
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class BrightnessCommand(Command):
    """Command for brightness changes."""
    def __init__(self, image_label, value):
        self.image_label = image_label
        self.value = value
        self.previous_image = image_label.image.copy()

    def execute(self):
        self.image_label.changeBrightness(self.value)
        self.image_label.repaint()

    def undo(self):
        self.image_label.image = self.previous_image.copy()
        self.image_label.setPixmap(QPixmap().fromImage(self.image_label.image))
        self.image_label.repaint()

class ContrastCommand(Command):
    """Command for contrast changes."""
    def __init__(self, image_label, value):
        self.image_label = image_label
        self.value = value
        self.previous_image = image_label.image.copy()

    def execute(self):
        self.image_label.changeContrast(self.value)
        self.image_label.repaint()

    def undo(self):
        self.image_label.image = self.previous_image.copy()
        self.image_label.setPixmap(QPixmap().fromImage(self.image_label.image))
        self.image_label.repaint()

class RotateCommand(Command):
    """Command for rotation."""
    def __init__(self, image_label, direction):
        self.image_label = image_label
        self.direction = direction
        self.previous_image = image_label.image.copy()

    def execute(self):
        self.image_label.rotateImage90(self.direction)
        self.image_label.repaint()

    def undo(self):
        self.image_label.image = self.previous_image.copy()
        self.image_label.setPixmap(QPixmap().fromImage(self.image_label.image))
        self.image_label.repaint()

class FlipCommand(Command):
    """Command for flipping."""
    def __init__(self, image_label, axis):
        self.image_label = image_label
        self.axis = axis
        self.previous_image = image_label.image.copy()

    def execute(self):
        self.image_label.flipImage(self.axis)
        self.image_label.repaint()

    def undo(self):
        self.image_label.image = self.previous_image.copy()
        self.image_label.setPixmap(QPixmap().fromImage(self.image_label.image))
        self.image_label.repaint()

class GrayscaleCommand(Command):
    """Command for grayscale conversion."""
    def __init__(self, image_label):
        self.image_label = image_label
        self.previous_image = image_label.image.copy()

    def execute(self):
        self.image_label.convertToGray()
        self.image_label.repaint()

    def undo(self):
        self.image_label.image = self.previous_image.copy()
        self.image_label.setPixmap(QPixmap().fromImage(self.image_label.image))
        self.image_label.repaint()

class RGBCommand(Command):
    """Command for RGB conversion."""
    def __init__(self, image_label):
        self.image_label = image_label
        self.previous_image = image_label.image.copy()

    def execute(self):
        self.image_label.convertToRGB()
        self.image_label.repaint()

    def undo(self):
        self.image_label.image = self.previous_image.copy()
        self.image_label.setPixmap(QPixmap().fromImage(self.image_label.image))
        self.image_label.repaint()

class SepiaCommand(Command):
    """Command for sepia conversion."""
    def __init__(self, image_label):
        self.image_label = image_label
        self.previous_image = image_label.image.copy()

    def execute(self):
        self.image_label.convertToSepia()
        self.image_label.repaint()

    def undo(self):
        self.image_label.image = self.previous_image.copy()
        self.image_label.setPixmap(QPixmap().fromImage(self.image_label.image))
        self.image_label.repaint()

class CropCommand(Command):
    """Command for cropping."""
    def __init__(self, image_label, crop_rect):
        self.image_label = image_label
        self.crop_rect = crop_rect
        self.previous_image = image_label.image.copy()

    def execute(self):
        if self.crop_rect.isValid():
            cropped = self.image_label.image.copy(self.crop_rect)
            self.image_label.image = QImage(cropped)
            self.image_label.setPixmap(QPixmap().fromImage(cropped))
            self.image_label.repaint()

    def undo(self):
        self.image_label.image = self.previous_image.copy()
        self.image_label.setPixmap(QPixmap().fromImage(self.image_label.image))
        self.image_label.repaint()

class ResizeCommand(Command):
    """Command for resizing."""
    def __init__(self, image_label):
        self.image_label = image_label
        self.previous_image = image_label.image.copy()

    def execute(self):
        self.image_label.resizeImage()
        self.image_label.repaint()

    def undo(self):
        self.image_label.image = self.previous_image.copy()
        self.image_label.setPixmap(QPixmap().fromImage(self.image_label.image))
        self.image_label.repaint()

class HueCommand(Command):
    """Command for hue changes."""
    def __init__(self, image_label, hue_shift):
        self.image_label = image_label
        self.hue_shift = hue_shift
        self.previous_image = image_label.image.copy()

    def execute(self):
        self.image_label.changeHue(self.hue_shift)
        self.image_label.repaint()

    def undo(self):
        self.image_label.image = self.previous_image.copy()
        self.image_label.setPixmap(QPixmap().fromImage(self.image_label.image))
        self.image_label.repaint()

class ZoomCommand(Command):
    """Command for zoom changes."""
    def __init__(self, photo_editor, zoom_value):
        self.photo_editor = photo_editor
        self.image_label = photo_editor.image_label
        self.previous_zoom = photo_editor.zoom_factor
        self.new_zoom = self.previous_zoom * zoom_value if zoom_value != 1.0 else 1.0
        self.zoom_value = zoom_value

    def execute(self):
        self.photo_editor.zoom_factor = self.new_zoom
        self.image_label.resize(self.new_zoom * self.image_label.pixmap().size())
        if self.zoom_value != 1.0:  # Normal size doesn't adjust scrollbars
            self.photo_editor.adjustScrollBar(self.photo_editor.scroll_area.horizontalScrollBar(), self.zoom_value)
            self.photo_editor.adjustScrollBar(self.photo_editor.scroll_area.verticalScrollBar(), self.zoom_value)
        self.photo_editor.updateActions()

    def undo(self):
        self.photo_editor.zoom_factor = self.previous_zoom
        self.image_label.resize(self.previous_zoom * self.image_label.pixmap().size())
        if self.zoom_value != 1.0:  # Normal size doesn't adjust scrollbars
            inverse_zoom = 1.0 / self.zoom_value
            self.photo_editor.adjustScrollBar(self.photo_editor.scroll_area.horizontalScrollBar(), inverse_zoom)
            self.photo_editor.adjustScrollBar(self.photo_editor.scroll_area.verticalScrollBar(), inverse_zoom)
        self.photo_editor.updateActions()