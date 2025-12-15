import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QFrame, QMessageBox, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QFontDatabase, QColor
from models.user_model import UserModel

class LoginWindow(QWidget):
    login_successful = pyqtSignal(tuple)
    register_requested = pyqtSignal()
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_model = UserModel(db)
        
        # bg_label
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        if os.path.exists("system_images/bg_pic.png"):
            self.pixmap = QPixmap("system_images/bg_pic.png")
            self.bg_label.setPixmap(self.pixmap)
        self.bg_label.lower()
        
        self.init_ui()
        self.showFullScreen()

    def resizeEvent(self, event):
        # Resize background to match window size
        self.bg_label.resize(self.size())
        return super().resizeEvent(event)
    
    def init_ui(self):
        self.setWindowTitle('Cuddle Corner')

        # Load custom font
        font_id = QFontDatabase.addApplicationFont(r"C:\Users\user\OneDrive\Documents\fonts\beachday.ttf")
        loaded_fonts = QFontDatabase.applicationFontFamilies(font_id)
        custom_font = loaded_fonts[0] if loaded_fonts else "Arial"

        if not loaded_fonts:
            print("Failed to load custom font!")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.setContentsMargins(0, 0, 100, 0)
        
        # Login frame
        login_frame = QFrame()
        login_frame.setObjectName('loginFrame')
        login_frame.setFixedSize(450, 500)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 120))
        login_frame.setGraphicsEffect(shadow)

        frame_layout = QVBoxLayout(login_frame)
        frame_layout.setSpacing(15)
        frame_layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel('Cuddle Corner')
        title.setObjectName('titleLabel')
        title.setStyleSheet('color: black; font-size: 35px; font-weight: bold;')
        if custom_font:
            title.setFont(QFont(custom_font, 30, QFont.Weight.Bold))
        else:
            title.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title)

        subtitle = QLabel('The Best Corner For Every Paw!')
        subtitle.setObjectName('subtitleLabel')
        subtitle.setStyleSheet('color: black; font-size: 15px;')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(subtitle)

        frame_layout.addSpacing(20)
        
        # Username
        username_label = QLabel('Username:')
        username_label.setStyleSheet('font-size: 15px; color: #2c3e50; font-weight: bold;')
        frame_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter your username')
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                color: black;
                font-family: Arial;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        frame_layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel('Password:')
        password_label.setStyleSheet('font-size: 15px; color: #2c3e50; font-weight: bold;')
        frame_layout.addWidget(password_label)

        # Password field with show/hide button
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter your password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                color: black;
                font-family: Arial;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        self.show_password_btn = QPushButton("Show")
        self.show_password_btn.setFixedSize(60, 40)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background: #f8f9fa;
                color: #667eea;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #667eea;
                color: white;
            }
        """)
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.show_password_btn)
        frame_layout.addLayout(password_layout)
        
        # Forgot password button
        extra_layout = QHBoxLayout()
        extra_layout.addStretch()
        
        self.forgot_password_btn = QPushButton("Forgot Password?")
        self.forgot_password_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #3498db;
                border: none;
                font-size: 13px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        self.forgot_password_btn.clicked.connect(self.handle_forgot_password)
        extra_layout.addWidget(self.forgot_password_btn)
        
        frame_layout.addLayout(extra_layout)
        
        # Login Button
        self.login_btn = QPushButton("Login")
        self.login_btn.setObjectName('loginBtn')
        self.login_btn.setFixedHeight(60)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #f9d162;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        frame_layout.addWidget(self.login_btn)
        
        # Register Link
        register_layout = QHBoxLayout()
        register_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        register_label = QLabel("Don't have an account?")
        register_label.setStyleSheet("color: #666; font-size: 14px;")
        self.register_btn = QPushButton("Register here")
        self.register_btn.setObjectName('registerBtn')
        self.register_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #667eea;
                border: none;
                font-size: 14px;
                font-weight: bold;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #764ba2;
            }
        """)
        self.register_btn.clicked.connect(self.register_requested.emit)
        
        register_layout.addWidget(register_label)
        register_layout.addWidget(self.register_btn)
        frame_layout.addLayout(register_layout)

        main_layout.addWidget(login_frame)
        self.setLayout(main_layout)
        
        self.username_input.setFocus()
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.handle_login)
    
    def toggle_password_visibility(self):
        if self.show_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("Show")
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return

        # Show loading state
        self.login_btn.setText("Logging in...")
        self.login_btn.setEnabled(False)

        # Authenticate password
        user = self.user_model.authenticate(username, password)

        if user:
            # Emit the signal with user data
            self.login_successful.emit((user['id'], user['username'], user['role']))
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")
            # Reset button state
            self.login_btn.setText("Login")
            self.login_btn.setEnabled(True)
    
    def handle_forgot_password(self):
        from ui.forgot_password_dialog import ForgotPasswordDialog
        dialog = ForgotPasswordDialog(self.user_model, self)
        dialog.exec()
    
    def clear_fields(self):
        self.username_input.clear()
        self.password_input.clear()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_password_btn.setChecked(False)
        self.show_password_btn.setText("Show")
        self.login_btn.setText("Login")
        self.login_btn.setEnabled(True)
        self.username_input.setFocus()
