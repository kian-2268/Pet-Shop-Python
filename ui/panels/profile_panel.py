from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QMessageBox, QGroupBox,
                             QFormLayout, QTextEdit)
from PyQt6.QtCore import Qt
from models.user_model import UserModel

class ProfilePanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.user_model = UserModel(db)
        self.init_ui()
        self.load_user_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("My Profile")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Profile form
        form_group = QGroupBox("Personal Information")
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        
        # Style inputs
        for widget in [self.first_name_input, self.last_name_input, self.email_input, self.phone_input]:
            widget.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    border: 2px solid #e1e1e1;
                    border-radius: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                }
            """)
        
        self.address_input.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        
        form_layout.addRow("First Name *:", self.first_name_input)
        form_layout.addRow("Last Name *:", self.last_name_input)
        form_layout.addRow("Email *:", self.email_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Address:", self.address_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Password change section
        password_group = QGroupBox("Change Password")
        password_layout = QFormLayout()
        password_layout.setSpacing(15)
        
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        for widget in [self.current_password_input, self.new_password_input, self.confirm_password_input]:
            widget.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    border: 2px solid #e1e1e1;
                    border-radius: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                }
            """)
        
        password_layout.addRow("Current Password:", self.current_password_input)
        password_layout.addRow("New Password:", self.new_password_input)
        password_layout.addRow("Confirm New Password:", self.confirm_password_input)
        
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        save_profile_btn = QPushButton("Save Profile")
        save_profile_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        save_profile_btn.clicked.connect(self.save_profile)
        
        change_password_btn = QPushButton("Change Password")
        change_password_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #219a52;
            }
        """)
        change_password_btn.clicked.connect(self.change_password)
        
        buttons_layout.addWidget(save_profile_btn)
        buttons_layout.addWidget(change_password_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def load_user_data(self):
        user = self.user_model.get_user_by_id(self.user_id)
        if user:
            self.first_name_input.setText(user['first_name'])
            self.last_name_input.setText(user['last_name'])
            self.email_input.setText(user['email'])
            self.phone_input.setText(user['phone'] or '')
            self.address_input.setText(user['address'] or '')
    
    def save_profile(self):
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.toPlainText().strip()
        
        # Validation
        if not first_name or not last_name or not email:
            QMessageBox.warning(self, "Error", "Please fill in all required fields")
            return
        
        user_data = (email, first_name, last_name, phone, address, self.user_id)
        
        if self.user_model.update_user(self.user_id, user_data):
            QMessageBox.information(self, "Success", "Profile updated successfully")
        else:
            QMessageBox.warning(self, "Error", "Failed to update profile")
    
    def change_password(self):
        current_password = self.current_password_input.text().strip()
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        if not current_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "Error", "Please fill in all password fields")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "New passwords do not match")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "Error", "New password must be at least 6 characters long")
            return
        
        # Verify current password
        user = self.user_model.get_user_by_id(self.user_id)
        # In a real application, you would verify the current password hash
        
        # Update password
        query = "UPDATE users SET password = %s WHERE id = %s"
        if self.db.execute_query(query, (new_password, self.user_id)):
            QMessageBox.information(self, "Success", "Password changed successfully")
            self.current_password_input.clear()
            self.new_password_input.clear()
            self.confirm_password_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Failed to change password")