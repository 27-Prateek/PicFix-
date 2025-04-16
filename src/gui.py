# src/gui.py
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QAction,
                             QSlider, QToolButton, QToolBar, QDockWidget, QMessageBox,
                             QGridLayout, QScrollArea, QFileDialog, QListWidget)
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QIcon, QImage, QPalette, QPainter
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from .image_label import imageLabel
from .commands import (CropCommand, ResizeCommand, RotateCommand, FlipCommand,
                      GrayscaleCommand, RGBCommand, SepiaCommand, BrightnessCommand,
                      ContrastCommand, ZoomCommand, HueCommand)
from .constants import ICON_PATH
from .database import add_image_edit, get_user_images
from PyQt5.QtWidgets import QPushButton, QDialog, QVBoxLayout




class PhotoEditorGUI(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username  # Store logged-in username
        self.undo_stack = []
        self.redo_stack = []
        self.zoom_factor = 1
        self.image = QImage()
        self.initializeUI()

    def initializeUI(self):
        self.setMinimumSize(300, 200)
        self.setWindowTitle(f"Photo Editor - {self.username}")
        self.showMaximized()
        self.createMainLabel()
        self.createEditingBar()
        self.createMenu()
        self.createToolBar()
        self.show()

    def createMenu(self):
        about_act = QAction('About', self)
        about_act.triggered.connect(self.aboutDialog)

        self.exit_act = QAction(QIcon(os.path.join(ICON_PATH, "exit.png")), 'Quit Photo Editor', self)
        self.exit_act.setShortcut('Ctrl+Q')
        self.exit_act.triggered.connect(self.close)

        self.open_act = QAction(QIcon(os.path.join(ICON_PATH, "open.png")), 'Open...', self)
        self.open_act.setShortcut('Ctrl+O')
        self.open_act.triggered.connect(self.openImage)

        self.print_act = QAction(QIcon(os.path.join(ICON_PATH, "print.png")), "Print...", self)
        self.print_act.setShortcut('Ctrl+P')
        self.print_act.setEnabled(False)
        self.print_act.triggered.connect(self.printImage)

        self.save_act = QAction(QIcon(os.path.join(ICON_PATH, "save.png")), "Save...", self)
        self.save_act.setShortcut('Ctrl+S')
        self.save_act.triggered.connect(self.saveImage)
        self.save_act.setEnabled(False)

        self.undo_act = QAction(QIcon(os.path.join(ICON_PATH, "undo.png")), "Undo", self)
        self.undo_act.setShortcut('Ctrl+Z')
        self.undo_act.triggered.connect(self.undo)
        self.undo_act.setEnabled(False)

        self.redo_act = QAction(QIcon(os.path.join(ICON_PATH, "redo.png")), "Redo", self)
        self.redo_act.setShortcut('Ctrl+Y')
        self.redo_act.triggered.connect(self.redo)
        self.redo_act.setEnabled(False)

        self.revert_act = QAction("Revert to Original", self)
        self.revert_act.triggered.connect(self.image_label.revertToOriginal)
        self.revert_act.setEnabled(False)

        self.crop_act = QAction(QIcon(os.path.join(ICON_PATH, "crop.png")), "Crop", self)
        self.crop_act.setShortcut('Shift+X')
        self.crop_act.triggered.connect(self.cropImage)

        self.resize_act = QAction(QIcon(os.path.join(ICON_PATH, "resize.png")), "Resize", self)
        self.resize_act.setShortcut('Shift+Z')
        self.resize_act.triggered.connect(self.resizeImage)

        self.rotate90_cw_act = QAction(QIcon(os.path.join(ICON_PATH, "rotate90_cw.png")), 'Rotate 90º CW', self)
        self.rotate90_cw_act.triggered.connect(lambda: self.rotateImage90("cw"))

        self.rotate90_ccw_act = QAction(QIcon(os.path.join(ICON_PATH, "rotate90_ccw.png")), 'Rotate 90º CCW', self)
        self.rotate90_ccw_act.triggered.connect(lambda: self.rotateImage90("ccw"))

        self.flip_horizontal = QAction(QIcon(os.path.join(ICON_PATH, "flip_horizontal.png")), 'Flip Horizontal', self)
        self.flip_horizontal.triggered.connect(lambda: self.flipImage("horizontal"))

        self.flip_vertical = QAction(QIcon(os.path.join(ICON_PATH, "flip_vertical.png")), 'Flip Vertical', self)
        self.flip_vertical.triggered.connect(lambda: self.flipImage('vertical'))

        self.zoom_in_act = QAction(QIcon(os.path.join(ICON_PATH, "zoom_in.png")), 'Zoom In', self)
        self.zoom_in_act.setShortcut('Ctrl++')
        self.zoom_in_act.triggered.connect(lambda: self.zoomOnImage(1.25))
        self.zoom_in_act.setEnabled(False)

        self.zoom_out_act = QAction(QIcon(os.path.join(ICON_PATH, "zoom_out.png")), 'Zoom Out', self)
        self.zoom_out_act.setShortcut('Ctrl+-')
        self.zoom_out_act.triggered.connect(lambda: self.zoomOnImage(0.8))
        self.zoom_out_act.setEnabled(False)

        self.normal_size_Act = QAction("Normal Size", self)
        self.normal_size_Act.setShortcut('Ctrl+=')
        self.normal_size_Act.triggered.connect(self.normalSize)
        self.normal_size_Act.setEnabled(False)

        self.history_act = QAction('Edit History', self)
        self.history_act.triggered.connect(self.showEditHistory)

        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        main_menu = menu_bar.addMenu('Photo Editor')
        main_menu.addAction(about_act)
        main_menu.addAction(self.history_act)
        main_menu.addSeparator()
        main_menu.addAction(self.exit_act)

        file_menu = menu_bar.addMenu('File')
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.save_act)
        file_menu.addSeparator()
        file_menu.addAction(self.print_act)

        edit_menu = menu_bar.addMenu('Edit')
        edit_menu.addAction(self.undo_act)
        edit_menu.addAction(self.redo_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.revert_act)

        tool_menu = menu_bar.addMenu('Tools')
        tool_menu.addAction(self.crop_act)
        tool_menu.addAction(self.resize_act)
        tool_menu.addSeparator()
        tool_menu.addAction(self.rotate90_cw_act)
        tool_menu.addAction(self.rotate90_ccw_act)
        tool_menu.addAction(self.flip_horizontal)
        tool_menu.addAction(self.flip_vertical)
        tool_menu.addSeparator()
        tool_menu.addAction(self.zoom_in_act)
        tool_menu.addAction(self.zoom_out_act)
        tool_menu.addAction(self.normal_size_Act)

        views_menu = menu_bar.addMenu('Views')
        views_menu.addAction(self.tools_menu_act)

    def createToolBar(self):
        tool_bar = QToolBar("Main Toolbar")
        tool_bar.setIconSize(QSize(26, 26))
        self.addToolBar(tool_bar)
        tool_bar.addAction(self.open_act)
        tool_bar.addAction(self.save_act)
        tool_bar.addAction(self.print_act)
        tool_bar.addSeparator()
        tool_bar.addAction(self.undo_act)
        tool_bar.addAction(self.redo_act)
        tool_bar.addSeparator()
        tool_bar.addAction(self.crop_act)
        tool_bar.addAction(self.resize_act)
        tool_bar.addSeparator()
        tool_bar.addAction(self.rotate90_ccw_act)
        tool_bar.addAction(self.rotate90_cw_act)
        tool_bar.addAction(self.flip_horizontal)
        tool_bar.addAction(self.flip_vertical)
        tool_bar.addSeparator()
        tool_bar.addAction(self.zoom_in_act)
        tool_bar.addAction(self.zoom_out_act)

    def createEditingBar(self):
        self.editing_bar = QDockWidget("Tools")
        self.editing_bar.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.editing_bar.setMinimumWidth(90)

        convert_to_grayscale = QToolButton()
        convert_to_grayscale.setIcon(QIcon(os.path.join(ICON_PATH, "grayscale.png")))
        convert_to_grayscale.clicked.connect(self.convertToGray)

        convert_to_RGB = QToolButton()
        convert_to_RGB.setIcon(QIcon(os.path.join(ICON_PATH, "rgb.png")))
        convert_to_RGB.clicked.connect(self.convertToRGB)

        convert_to_sepia = QToolButton()
        convert_to_sepia.setIcon(QIcon(os.path.join(ICON_PATH, "sepia.png")))
        convert_to_sepia.clicked.connect(self.convertToSepia)

        change_hue = QToolButton()
        change_hue.setIcon(QIcon(os.path.join(ICON_PATH, "hue.png")))
        change_hue.clicked.connect(self.changeHue)

        brightness_label = QLabel("Brightness")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-60,60)
        self.brightness_slider.setTickInterval(35)
        self.brightness_slider.setTickPosition(QSlider.TicksAbove)
        self.brightness_slider.valueChanged.connect(self.changeBrightness)

        contrast_label = QLabel("Contrast")
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-30, 30)
        self.contrast_slider.setTickInterval(35)
        self.contrast_slider.setTickPosition(QSlider.TicksAbove)
        self.contrast_slider.valueChanged.connect(self.changeContrast)

        hue_label = QLabel("Hue")
        self.hue_slider = QSlider(Qt.Horizontal)
        self.hue_slider.setRange(-180, 180)
        self.hue_slider.setTickInterval(30)
        self.hue_slider.setTickPosition(QSlider.TicksAbove)
        self.hue_slider.valueChanged.connect(self.changeHue)

        editing_grid = QGridLayout()
        editing_grid.addWidget(convert_to_grayscale, 1, 0)
        editing_grid.addWidget(convert_to_RGB, 1, 1)
        editing_grid.addWidget(convert_to_sepia, 2, 0)
        editing_grid.addWidget(change_hue, 2, 1)
        editing_grid.addWidget(brightness_label, 3, 0)
        editing_grid.addWidget(self.brightness_slider, 4, 0, 1, 2)
        editing_grid.addWidget(contrast_label, 5, 0)
        editing_grid.addWidget(self.contrast_slider, 6, 0, 1, 2)
        editing_grid.addWidget(hue_label, 7, 0)
        editing_grid.addWidget(self.hue_slider, 8, 0, 1, 2)
        editing_grid.setRowStretch(9, 10)

        container = QWidget()
        container.setLayout(editing_grid)
        self.editing_bar.setWidget(container)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.editing_bar)
        self.tools_menu_act = self.editing_bar.toggleViewAction()

    def createMainLabel(self):
        self.image_label = imageLabel(self)
        self.image_label.resize(self.image_label.pixmap().size())
        self.scroll_area = QScrollArea()
        self.scroll_area.setBackgroundRole(QPalette.Dark)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        self.setCentralWidget(self.scroll_area)

    # def openImage(self):
    #     """Open an image and log it to the database."""
    #     file_name, _ = QFileDialog.getOpenFileName(
    #         self, "Open Image File", "",
    #         "Images (*.png *.xpm *.jpg *.bmp *.gif)")
    #     if file_name:
    #         self.image_label.openImage(file_name)
    #         add_image_edit(file_name, self.username)
    #         self.updateActions()
    def saveOriginalImage(self, file_name):
    # Store the original image for later use (e.g., reset or undo operations)
        self.original_image = QImage(file_name)  # Load image using QImage for PyQt
    # Optionally, you could save it to a file or keep it in memory
    # Example: self.original_image.save("original_backup.png") if saving to disk

    def openImage(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp )"
        )
        if file_name:
            if self.image_label.openImage(file_name):  # Line 249
                self.setWindowTitle(f"Photo Editor - {self.username} - {file_name}")
                self.saveOriginalImage(file_name)




    # def saveImage(self):
    #    self.image_label.saveImage()

    # def saveImage(self):
    #     """Save the current image and log it to the database."""
    #     file_name = self.image_label.saveImage()
    #     if file_name:
    #         add_image_edit(file_name, self.username)
    #         self.updateActions()

    def saveImage(self):
        """Save the current image and log it to the database."""
        file_name = self.image_label.saveImage()
        if file_name:
            add_image_edit(file_name, self.username)
            self.updateActions()

    def printImage(self):
        """Handle printing of the current image."""
        if not self.image_label.image.isNull():
            printer = QPrinter(QPrinter.HighResolution)
            print_dialog = QPrintDialog(printer, self)
            if print_dialog.exec_() == QPrintDialog.Accepted:
                painter = QPainter(printer)
                rect = painter.viewport()
                size = self.image_label.image.size()
                size.scale(rect.size(), Qt.KeepAspectRatio)
                painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
                painter.setWindow(self.image_label.image.rect())
                painter.drawImage(0, 0, self.image_label.image)
                painter.end()
        else:
            QMessageBox.warning(self, "No Image", "There is no image to print.", QMessageBox.Ok)

    def showEditHistory(self):
        """Show the user's edit history."""
        images = get_user_images(self.username)
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle(f"Edit History for {self.username}")
        history_dialog.setFixedSize(400, 300)
        layout = QVBoxLayout()

        list_widget = QListWidget()
        list_widget.addItems(images if images else ["No images edited yet."])
        layout.addWidget(list_widget)

        close_button = QPushButton("Close")
        close_button.clicked.connect(history_dialog.accept)
        layout.addWidget(close_button)

        history_dialog.setLayout(layout)
        history_dialog.exec_()

    def executeCommand(self, command):
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()
        self.updateActions()

    def undo(self):
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)
            self.updateActions()

    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)
            self.updateActions()

    def updateActions(self):
        has_image = not self.image_label.image.isNull()
        self.save_act.setEnabled(has_image)
        self.revert_act.setEnabled(has_image)
        self.zoom_in_act.setEnabled(has_image and self.zoom_factor < 4.0)
        self.zoom_out_act.setEnabled(has_image and self.zoom_factor > 0.333)
        self.normal_size_Act.setEnabled(has_image)
        self.undo_act.setEnabled(bool(self.undo_stack))
        self.redo_act.setEnabled(bool(self.redo_stack))
        self.print_act.setEnabled(has_image)

    def cropImage(self):
        if not self.image_label.image.isNull():
            if self.image_label.crop_rect.isValid():
                command = CropCommand(self.image_label, self.image_label.crop_rect)
                self.executeCommand(command)
                self.image_label.crop_rect = QRect()
                if self.image_label.rubber_band:
                    self.image_label.rubber_band.hide()
            else:
                QMessageBox.warning(self, "No Selection",
                                    "Please drag a rectangle over the image to crop.", QMessageBox.Ok)

    def resizeImage(self):
        if not self.image_label.image.isNull():
            command = ResizeCommand(self.image_label)
            self.executeCommand(command)

    def rotateImage90(self, direction):
        if not self.image_label.image.isNull():
            command = RotateCommand(self.image_label, direction)
            self.executeCommand(command)

    def flipImage(self, axis):
        if not self.image_label.image.isNull():
            command = FlipCommand(self.image_label, axis)
            self.executeCommand(command)

    def convertToGray(self):
        if not self.image_label.image.isNull():
            command = GrayscaleCommand(self.image_label)
            self.executeCommand(command)

    def convertToRGB(self):
        if not self.image_label.image.isNull():
            command = RGBCommand(self.image_label)
            self.executeCommand(command)

    def convertToSepia(self):
        if not self.image_label.image.isNull():
            command = SepiaCommand(self.image_label)
            self.executeCommand(command)

    def changeBrightness(self, value):
        if not self.image_label.image.isNull():
            command = BrightnessCommand(self.image_label, value)
            self.executeCommand(command)

    def changeContrast(self, value):
        if not self.image_label.image.isNull():
            command = ContrastCommand(self.image_label, value)
            self.executeCommand(command)

    def changeHue(self, value=None):
        if not self.image_label.image.isNull():
            hue_shift = value if value is not None else 30
            command = HueCommand(self.image_label, hue_shift)
            self.executeCommand(command)

    def zoomOnImage(self, zoom_value):
        if not self.image_label.image.isNull():
            command = ZoomCommand(self, zoom_value)
            self.executeCommand(command)

    def normalSize(self):
        if not self.image_label.image.isNull():
            command = ZoomCommand(self, 1.0)
            self.executeCommand(command)

    def adjustScrollBar(self, scroll_bar, value):
        scroll_bar.setValue(int(value * scroll_bar.value() + (value - 1) * scroll_bar.pageStep() / 2))

    def aboutDialog(self):
        QMessageBox.about(self, "About PicFix",
                          "PicFix - Minimalist Photo Editing Platform\n ")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        if event.key() == Qt.Key_F1:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()

    def closeEvent(self, event):
        pass