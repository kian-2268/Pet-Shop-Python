from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox,
                             QCheckBox, QScrollArea, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from models.user_model import UserModel

class RegisterDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_model = UserModel(db)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Register New Account")
        self.setModal(True)
        self.resize(500, 400)  

        self.setStyleSheet("background-color: #f9fafb; color: black;")
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)
        
        # Create container widget for scroll area
        container = QWidget()
        scroll_area.setWidget(container)
        
        # Main layout for the dialog
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        
        # Layout for the container 
        layout = QVBoxLayout(container)
        layout.setSpacing(5)
        layout.setContentsMargins(20, 10, 20, 10)  # Add some margins

        # Logo pic
        logo_path = "system_images/register.png"

        logo = QLabel()
        pix = QPixmap(logo_path)
        logo.setPixmap(pix.scaledToHeight(100, Qt.TransformationMode.SmoothTransformation)) #scales img
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        
        # Title
        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: black; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Form fields
        fields = [
            ("First Name *:", "first_name"),
            ("Last Name *:", "last_name"),
            ("Email *:", "email"),
            ("Phone:", "phone"),
            ("Address:", "address"),
            ("Username *:", "username"),
            ("Password *:", "password"),
            ("Confirm Password *:", "confirm_password")
        ]
        
        self.inputs = {}
        
        for label_text, field_name in fields:
            field_layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("color: #666; font-size: 14px;")
            
            if "password" in field_name:
                input_field = QLineEdit()
                input_field.setEchoMode(QLineEdit.EchoMode.Password)
            else:
                input_field = QLineEdit()
            
            input_field.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    border: 2px solid #e1e1e1;
                    border-radius: 8px;
                    font-size: 14px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border-color: #667eea;
                }
            """)
            
            field_layout.addWidget(label)
            field_layout.addWidget(input_field)
            layout.addLayout(field_layout)
            
            self.inputs[field_name] = input_field
        
        # Show password checkbox
        self.show_password = QCheckBox("Show passwords")
        self.show_password.setStyleSheet("color: #666; font-size: 14px;")
        self.show_password.toggled.connect(self.toggle_passwords_visibility)
        layout.addWidget(self.show_password)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        register_btn = QPushButton("Register")
        register_btn.setStyleSheet("""
            QPushButton {
                background: #e67e22;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #f9d162;
            }
        """)
        register_btn.clicked.connect(self.register)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(register_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        # Add some stretch at the bottom to push content up
        layout.addStretch()
    
    def toggle_passwords_visibility(self, checked):
        mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self.inputs['password'].setEchoMode(mode)
        self.inputs['confirm_password'].setEchoMode(mode)
    
    def register(self):
        # Get form data
        data = {key: field.text().strip() for key, field in self.inputs.items()}
    
        # Validation
        required_fields = ['first_name', 'last_name', 'email', 'username', 'password']
        for field in required_fields:
            if not data[field]:
                QMessageBox.warning(self, "Error", f"{field.replace('_', ' ').title()} is required")
                return
    
        if data['password'] != data['confirm_password']:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
    
        if len(data['password']) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters long")
            return
    
        # Prepare user data - role as 'customer'
        user_data = (
            data['username'],
            data['password'],
            data['email'],
            data['first_name'],
            data['last_name'],
            data.get('phone', ''),
            data.get('address', ''),
            'customer' 
        )
    
        try:
            result = self.user_model.create_user(*user_data)
            if result:
                QMessageBox.information(self, "Success", "Account created successfully!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to create account. Username or email may already exist.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
