# src/image_label.py
from PyQt5.QtWidgets import QLabel, QMessageBox, QSizePolicy, QRubberBand
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QImage, QPixmap, QTransform, QPalette, qRgb, QColor 
from PyQt5.QtWidgets import QFileDialog



class imageLabel(QLabel):
    """Subclass of QLabel for displaying image."""
    def __init__(self, parent, image=None):
        super().__init__(parent)
        self.parent = parent
        self.image = QImage() if image is None else image
        self.original_image = self.image
        self.rubber_band = None
        self.crop_rect = QRect()
        self.origin = None
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setScaledContents(True)
        self.setPixmap(QPixmap().fromImage(self.image))
        self.setAlignment(Qt.AlignCenter)

    def openImage(self, file_name):
        """Load a new image from file_name into the label."""
        if file_name:
            self.image = QImage(file_name)
            if self.image.isNull():
                QMessageBox.information(self, "Error", f"Unable to open image: {file_name}", QMessageBox.Ok)
                return False
            self.original_image = self.image.copy()
            self.setPixmap(QPixmap().fromImage(self.image))
            self.resize(self.pixmap().size())
            self.parent.zoom_factor = 1
            self.parent.brightness_slider.setValue(0)
            self.parent.undo_stack.clear()
            self.parent.redo_stack.clear()
            self.parent.print_act.setEnabled(True)
            self.parent.updateActions()
            return True
        return False

    # def saveImage(self):
    #     """Save the image displayed in the label."""
    #     if not self.image.isNull():
    #         image_file, _ = QFileDialog.getSaveFileName(
    #             self, "Save Image", "",
    #             "PNG Files (*.png);;JPG Files (*.jpeg *.jpg );;Bitmap Files (*.bmp);;GIF Files (*.gif)"
    #         )
    #         if image_file:
    #             self.image.save(image_file)
    #         else:
    #             QMessageBox.information(self, "Error", "Unable to save image.", QMessageBox.Ok)
    #     else:
    #         QMessageBox.information(self, "Empty Image", "There is no image to save.", QMessageBox.Ok)


    # def saveImage(self):
    #     file_name, _ = QFileDialog.getSaveFileName(
    #         self,
    #         "Save Image",
    #         "",
    #         "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
    #     )
    #     if file_name:
    #         self.image_label.saveImage(file_name)  # Line 276, causing the error

    # def saveImage(self):
    #     """Save the image displayed in the label."""
    #     if not self.image.isNull():
    #         image_file, _ = QFileDialog.getSaveFileName(
    #             self,
    #             "Save Image",
    #             "",
    #             "PNG Files (*.png);;JPG Files (*.jpeg *.jpg);;Bitmap Files (*.bmp);;GIF Files (*.gif)"
    #         )
    #         if image_file:
    #             self.image.save(image_file)
    #         else:
    #             # Only show error if dialog wasn't canceled
    #             if image_file is not None:
    #                 QMessageBox.information(self, "Error", "Unable to save image.", QMessageBox.Ok)
    #     else:
    #         QMessageBox.information(self, "Empty Image", "There is no image to save.", QMessageBox.Ok)


    # def saveImage(self):
    #     """Save the image displayed in the label and return the file path."""
    #     if not self.image.isNull():
    #         image_file, _ = QFileDialog.getSaveFileName(
    #             self,
    #             "Save Image",
    #             "",
    #             "PNG Files (*.png);;JPG Files (*.jpeg *.jpg);;Bitmap Files (*.bmp);;GIF Files (*.gif)"
    #         )
    #         if image_file:
    #             self.image.save(image_file)
    #             return image_file  # Return the saved file path
    #         else:
    #             # Only show error if dialog wasn't canceled
    #             if image_file is not None:
    #                 QMessageBox.information(self, "Error", "Unable to save image.", QMessageBox.Ok)
    #     else:
    #         QMessageBox.information(self, "Empty Image", "There is no image to save.", QMessageBox.Ok)
    #     return None  # Return None if saving fails or is canceled

    def saveImage(self):
        """Save the image displayed in the label and return the file path."""
        if not self.image.isNull():
            image_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save Image",
                "",
                "PNG Files (*.png);;JPG Files (*.jpeg *.jpg);;Bitmap Files (*.bmp)"
            )
            if image_file:
                self.image.save(image_file)
                return image_file  # Return the saved file path
            else:
                # Only show error if dialog wasn't canceled
                if image_file is not None:
                    QMessageBox.information(self, "Error", "Unable to save image.", QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Empty Image", "There is no image to save.", QMessageBox.Ok)
        return None  # Return None if saving fails or is canceled



    def clearImage(self):
        """Clear the current image."""
        # TODO: If image is not null ask to save image first.
        pass

    def revertToOriginal(self):
        """Revert the image back to original image."""
        if not self.image.isNull():
            reply = QMessageBox.question(
                self, "Revert to Original",
                "Are you sure you want to revert to the original image? All changes will be lost.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.image = self.original_image.copy()
                self.setPixmap(QPixmap().fromImage(self.image))
                self.repaint()
                self.parent.undo_stack.clear()
                self.parent.redo_stack.clear()
                self.parent.updateActions()

    def resizeImage(self):
        """Resize image."""
        if not self.image.isNull():
            resize = QTransform().scale(0.5, 0.5)
            pixmap = QPixmap(self.image)
            resized_image = pixmap.transformed(resize, mode=Qt.SmoothTransformation)
            self.image = QImage(resized_image)
            self.setPixmap(resized_image)
            self.setScaledContents(True)
            self.repaint()

    def rotateImage90(self, direction):
        """Rotate image 90º clockwise or counterclockwise."""
        if not self.image.isNull():
            if direction == "cw":
                transform90 = QTransform().rotate(90)
            elif direction == "ccw":
                transform90 = QTransform().rotate(-90)
            pixmap = QPixmap(self.image)
            rotated = pixmap.transformed(transform90, mode=Qt.SmoothTransformation)
            self.resize(self.image.height(), self.image.width())
            self.image = QImage(rotated)
            self.setPixmap(rotated.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            self.repaint()

    def flipImage(self, axis):
        """Mirror the image across the horizontal or vertical axis."""
        if not self.image.isNull():
            if axis == "horizontal":
                flip_h = QTransform().scale(-1, 1)
                pixmap = QPixmap(self.image)
                flipped = pixmap.transformed(flip_h)
            elif axis == "vertical":
                flip_v = QTransform().scale(1, -1)
                pixmap = QPixmap(self.image)
                flipped = pixmap.transformed(flip_v)
            self.image = QImage(flipped)
            self.setPixmap(flipped)
            self.repaint()

    def convertToGray(self):
        """Convert image to grayscale."""
        if not self.image.isNull():
            converted_img = self.image.convertToFormat(QImage.Format_Grayscale16)
            self.image = QImage(converted_img)
            self.setPixmap(QPixmap().fromImage(converted_img))
            self.repaint()

    def convertToRGB(self):
        """Convert image to RGB format."""
        if not self.image.isNull():
            converted_img = self.image.convertToFormat(QImage.Format_RGB32)
            self.image = QImage(converted_img)
            self.setPixmap(QPixmap().fromImage(converted_img))
            self.repaint()

    # def convertToSepia(self):
    #     """Convert image to sepia filter."""
    #     if not self.image.isNull():
    #         for row_pixel in range(self.image.width()):
    #             for col_pixel in range(self.image.height()):
    #                 current_val = QColor(self.image.pixel(row_pixel, col_pixel))
    #                 red = current_val.red()
    #                 green = current_val.green()
    #                 blue = current_val.blue()
    #                 new_red = int(0.393 * red + 0.769 * green + 0.189 * blue)
    #                 new_green = int(0.349 * red + 0.686 * green + 0.168 * blue)
    #                 new_blue = int(0.272 * red + 0.534 * green + 0.131 * blue)
    #                 red = min(new_red, 255)
    #                 green = min(new_green, 255)
    #                 blue = min(new_blue, 255)
    #                 new_value = qRgb(red, green, blue)
    #                 self.image.setPixel(row_pixel, col_pixel, new_value)
    #         self.setPixmap(QPixmap().fromImage(self.image))
    #         self.repaint()

    def convertToSepia(self):
        """Convert image to sepia filter."""
        if not self.image.isNull():
            # Convert image to RGB32 format for consistent pixel manipulation
            sepia_image = self.image.convertToFormat(QImage.Format_RGB32)
            
            for row_pixel in range(sepia_image.width()):
                for col_pixel in range(sepia_image.height()):
                    current_val = QColor(sepia_image.pixel(row_pixel, col_pixel))
                    red = current_val.red()
                    green = current_val.green()
                    blue = current_val.blue()
                    
                    # Apply sepia transformation
                    new_red = min(int(0.393 * red + 0.769 * green + 0.189 * blue), 255)
                    new_green = min(int(0.349 * red + 0.686 * green + 0.168 * blue), 255)
                    new_blue = min(int(0.272 * red + 0.534 * green + 0.131 * blue), 255)
                    
                    # Set pixel with valid QRgb value
                    sepia_image.setPixel(row_pixel, col_pixel, qRgb(new_red, new_green, new_blue))
            
            # Update the image and pixmap
            self.image = sepia_image
            self.setPixmap(QPixmap.fromImage(self.image))
            self.repaint()

    # def changeBrightness(self, value):
    #     """Change brightness of the image."""
    #     if not self.image.isNull() and -255 <= value <= 255:
    #         for row_pixel in range(self.image.width()):
    #             for col_pixel in range(self.image.height()):
    #                 current_val = QColor(self.image.pixel(row_pixel, col_pixel))
    #                 red = current_val.red()
    #                 green = current_val.green()
    #                 blue = current_val.blue()
    #                 new_red = max(0, min(255, red + value))
    #                 new_green = max(0, min(255, green + value))
    #                 new_blue = max(0, min(255, blue + value))
    #                 new_value = qRgb(new_red, new_green, new_blue)
    #                 self.image.setPixel(row_pixel, col_pixel, new_value)
    #         self.setPixmap(QPixmap().fromImage(self.image))
    #         self.repaint()



    def changeBrightness(self, value):
        """Change brightness of the image."""
        if not self.image.isNull():
            # Convert image to RGB32 format for consistent pixel manipulation
            bright_image = self.image.convertToFormat(QImage.Format_RGB32)
            
            for row_pixel in range(bright_image.width()):
                for col_pixel in range(bright_image.height()):
                    current_val = QColor(bright_image.pixel(row_pixel, col_pixel))
                    red = current_val.red()
                    green = current_val.green()
                    blue = current_val.blue()
                    
                    # Apply brightness adjustment
                    new_red = max(0, min(255, red + value))
                    new_green = max(0, min(255, green + value))
                    new_blue = max(0, min(255, blue + value))
                    
                    # Set pixel with valid QRgb value
                    bright_image.setPixel(row_pixel, col_pixel, qRgb(new_red, new_green, new_blue))
            
            # Update the image and pixmap
            self.image = bright_image
            self.setPixmap(QPixmap.fromImage(self.image))
            self.repaint()

    # def changeContrast(self, contrast):
    #     """Change the contrast of the pixels in the image."""
    #     if not self.image.isNull():
    #         factor = float(259 * (contrast + 255) / (255 * (259 - contrast)))
    #         for row_pixel in range(self.image.width()):
    #             for col_pixel in range(self.image.height()):
    #                 current_val = QColor(self.image.pixel(row_pixel, col_pixel))
    #                 red = current_val.red()
    #                 green = current_val.green()
    #                 blue = current_val.blue()
    #                 new_red = max(0, min(255, int(factor * (red - 128) + 128)))
    #                 new_green = max(0, min(255, int(factor * (green - 128) + 128)))
    #                 new_blue = max(0, min(255, int(factor * (blue - 128) + 128)))
    #                 new_value = qRgb(new_red, new_green, new_blue)
    #                 self.image.setPixel(row_pixel, col_pixel, new_value)
    #         self.setPixmap(QPixmap().fromImage(self.image))
    #         self.repaint()

    def changeContrast(self, contrast):
        """Change the contrast of the pixels in the image."""
        if not self.image.isNull():
            # Convert image to RGB32 format for consistent pixel manipulation
            contrast_image = self.image.convertToFormat(QImage.Format_RGB32)
            
            # Calculate contrast factor
            factor = float(259 * (contrast + 255) / (255 * (259 - contrast)))
            
            for row_pixel in range(contrast_image.width()):
                for col_pixel in range(contrast_image.height()):
                    current_val = QColor(contrast_image.pixel(row_pixel, col_pixel))
                    red = current_val.red()
                    green = current_val.green()
                    blue = current_val.blue()
                    
                    # Apply contrast adjustment
                    new_red = max(0, min(255, int(factor * (red - 128) + 128)))
                    new_green = max(0, min(255, int(factor * (green - 128) + 128)))
                    new_blue = max(0, min(255, int(factor * (blue - 128) + 128)))
                    
                    # Set pixel with valid QRgb value
                    contrast_image.setPixel(row_pixel, col_pixel, qRgb(new_red, new_green, new_blue))
            
            # Update the image and pixmap
            self.image = contrast_image
            self.setPixmap(QPixmap.fromImage(self.image))
            self.repaint()

    # def changeHue(self, hue_shift):
    #     """Shift the hue of the image by hue_shift degrees (0-360)."""
    #     if not self.image.isNull():
    #         for row_pixel in range(self.image.width()):
    #             for col_pixel in range(self.image.height()):
    #                 current_val = QColor(self.image.pixel(row_pixel, col_pixel))
    #                 hue = (current_val.hue() + hue_shift) % 360
    #                 current_val.setHsv(hue, current_val.saturation(), current_val.value(), current_val.alpha())
    #                 self.image.setPixelColor(row_pixel, col_pixel, current_val)
    #         self.setPixmap(QPixmap().fromImage(self.image))
    #         self.repaint()

    def changeHue(self, hue_shift):
        """Shift the hue of the image by hue_shift degrees (0-360)."""
        if not self.image.isNull():
            # Convert image to RGB32 format for consistent color manipulation
            hue_image = self.image.convertToFormat(QImage.Format_RGB32)
            
            for row_pixel in range(hue_image.width()):
                for col_pixel in range(hue_image.height()):
                    current_val = QColor(hue_image.pixel(row_pixel, col_pixel))
                    # Shift hue while preserving saturation and value
                    hue = (current_val.hue() + hue_shift) % 360
                    current_val.setHsv(hue, current_val.saturation(), current_val.value(), current_val.alpha())
                    hue_image.setPixelColor(row_pixel, col_pixel, current_val)
            
            # Update the image and pixmap
            self.image = hue_image
            self.setPixmap(QPixmap.fromImage(self.image))
            self.repaint()

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.LeftButton and not self.image.isNull():
            self.origin = event.pos()
            if not self.rubber_band:
                self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        """Handle mouse move event."""
        if self.rubber_band and self.rubber_band.isVisible():
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        """Handle when the mouse is released."""
        if event.button() == Qt.LeftButton and self.rubber_band and self.rubber_band.isVisible():
            self.crop_rect = self.rubber_band.geometry()
            zoom_factor = self.parent.zoom_factor
            if zoom_factor != 1.0:
                self.crop_rect = QRect(
                    int(self.crop_rect.x() / zoom_factor),
                    int(self.crop_rect.y() / zoom_factor),
                    int(self.crop_rect.width() / zoom_factor),
                    int(self.crop_rect.height() / zoom_factor)
                )
            self.rubber_band.hide()