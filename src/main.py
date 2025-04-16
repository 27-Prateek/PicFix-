import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from .gui import PhotoEditorGUI
from PyQt5.QtWidgets import QDialog
from .login import LoginDialog

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontShowIconsInMenus, False)
    
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        window = PhotoEditorGUI(login_dialog.getCurrentUsername())
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)