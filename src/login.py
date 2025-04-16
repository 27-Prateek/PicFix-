
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QComboBox, QWidget)

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .database import (init_database, add_user, verify_user, get_security_question,
                      reset_password)

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login to Photo Editor")
        self.setFixedSize(400, 500)
        self.current_username = None
        try:
            init_database()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to initialize database: {str(e)}")
            self.reject()
            return
        self.setupUI()

    def setupUI(self):
        """Set up the login dialog UI with a modern design."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Card widget
        card = QWidget()
        card.setObjectName("card")
        card_layout = QVBoxLayout()
        card_layout.setSpacing(10)
        card.setLayout(card_layout)

        # Title
        title_label = QLabel("Welcome to PicFix")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title")
        card_layout.addWidget(title_label)

        # Username field
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        username_label.setFixedWidth(100)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        card_layout.addLayout(username_layout)

        # Password field
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setFixedWidth(100)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        card_layout.addLayout(password_layout)

        # Security question
        security_question_layout = QHBoxLayout()
        security_question_label = QLabel("Security Question:")
        security_question_label.setFixedWidth(100)
        self.security_question = QComboBox()
        self.security_question.addItems([
            "What is your mother's maiden name?",
            "What was the name of your first pet?",
            "What is your favorite book?"
        ])
        security_question_layout.addWidget(security_question_label)
        security_question_layout.addWidget(self.security_question)
        card_layout.addLayout(security_question_layout)

        # Security answer
        security_answer_layout = QHBoxLayout()
        security_answer_label = QLabel("Security Answer:")
        security_answer_label.setFixedWidth(100)
        self.security_answer_input = QLineEdit()
        self.security_answer_input.setPlaceholderText("Enter answer")  
        security_answer_layout.addWidget(security_answer_label)
        security_answer_layout.addWidget(self.security_answer_input)
        card_layout.addLayout(security_answer_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.verifyCredentials)
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.registerUser)
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        card_layout.addLayout(button_layout)

        # Forgot Password
        extra_button_layout = QHBoxLayout()
        self.forgot_password_button = QPushButton("Forgot Password")
        self.forgot_password_button.clicked.connect(self.handleForgotPassword)
        extra_button_layout.addWidget(self.forgot_password_button)
        card_layout.addLayout(extra_button_layout)

        layout.addWidget(card)
        layout.addStretch()
        self.setLayout(layout)

        # Apply modern stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #333;
            }
            #card {
                background-color: #F5F5F5;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #CCC;
            }
            #title {
                color: #222;
                margin-bottom: 20px;
            }
            QLabel {
                color: #222;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                background-color: #FFF;
                border: 1px solid #CCC;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #007BFF;
                outline: none;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton#forgotButton {
                background-color: #6C757D;
            }
            QPushButton#forgotButton:hover {
                background-color: #5a6268;
            }
        """)
        self.forgot_password_button.setObjectName("forgotButton")

    def verifyCredentials(self):
        """Verify the entered username and password."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        try:
            if verify_user(username, password):
                self.current_username = username
                self.accept()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.", QMessageBox.Ok)
                self.password_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login error: {str(e)}")

    def registerUser(self):
        """Register a new user."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        question = self.security_question.currentText()
        answer = self.security_answer_input.text().strip()
        if not username or not password or not answer:
            QMessageBox.warning(self, "Registration Failed", "Please fill in all fields.", QMessageBox.Ok)
            return
        try:
            if add_user(username, password, question, answer):
                QMessageBox.information(self, "Registration Successful", "You can now log in with your credentials.")
                self.username_input.clear()
                self.password_input.clear()
                self.security_answer_input.clear()
            else:
                QMessageBox.warning(self, "Registration Failed", "Username already exists.", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration error: {str(e)}")

    def handleForgotPassword(self):
        """Handle forgot password by verifying security question."""
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Please enter a username.", QMessageBox.Ok)
            return
        try:
            question_answer = get_security_question(username)
            if not question_answer:
                QMessageBox.warning(self, "No Account", "No account found for this username.", QMessageBox.Ok)
                return
            question, _ = question_answer
            forgot_dialog = QDialog(self)
            forgot_dialog.setWindowTitle("Reset Password")
            forgot_dialog.setFixedSize(350, 300)
            forgot_layout = QVBoxLayout()
            forgot_layout.setContentsMargins(20, 20, 20, 20)
            card = QWidget()
            card.setObjectName("card")
            card_layout = QVBoxLayout()
            card_layout.setSpacing(10)
            card.setLayout(card_layout)
            title_label = QLabel("Reset Your Password")
            title_label.setFont(QFont("Arial", 16, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setObjectName("title")
            card_layout.addWidget(title_label)
            question_label = QLabel(f"Question: {question}")
            question_label.setWordWrap(True)
            card_layout.addWidget(question_label)
            answer_layout = QHBoxLayout()
            answer_label = QLabel("Answer:")
            answer_label.setFixedWidth(100)
            answer_input = QLineEdit()
            answer_input.setPlaceholderText("Enter your answer")
            answer_layout.addWidget(answer_label)
            answer_layout.addWidget(answer_input)
            card_layout.addLayout(answer_layout)
            new_password_layout = QHBoxLayout()
            new_password_label = QLabel("New Password:")
            new_password_label.setFixedWidth(100)
            new_password_input = QLineEdit()
            new_password_input.setEchoMode(QLineEdit.Password)
            new_password_input.setPlaceholderText("Enter new password")
            new_password_layout.addWidget(new_password_label)
            new_password_layout.addWidget(new_password_input)
            card_layout.addLayout(new_password_layout)
            button_layout = QHBoxLayout()
            submit_button = QPushButton("Submit")
            submit_button.setObjectName("primaryButton")
            cancel_button = QPushButton("Cancel")
            cancel_button.setObjectName("forgotButton")
            button_layout.addWidget(submit_button)
            button_layout.addWidget(cancel_button)
            card_layout.addLayout(button_layout)
            forgot_layout.addWidget(card)
            forgot_layout.addStretch()
            forgot_dialog.setLayout(forgot_layout)
            forgot_dialog.setStyleSheet(self.styleSheet().replace("QPushButton", "QPushButton#primaryButton"))
            def submit_reset():
                answer = answer_input.text().strip()
                new_password = new_password_input.text().strip()
                try:
                    if reset_password(username, new_password, answer):
                        QMessageBox.information(forgot_dialog, "Success", "Password reset successfully.")
                        forgot_dialog.accept()
                    else:
                        QMessageBox.warning(forgot_dialog, "Error", "Incorrect answer or empty password.", QMessageBox.Ok)
                except Exception as e:
                    QMessageBox.critical(forgot_dialog, "Error", f"Reset error: {str(e)}")
            submit_button.clicked.connect(submit_reset)
            cancel_button.clicked.connect(forgot_dialog.reject)
            forgot_dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Forgot password error: {str(e)}")

    def getCurrentUsername(self):
        """Return the logged-in username."""
        return self.current_username