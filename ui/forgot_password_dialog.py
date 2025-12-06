import secrets
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from datetime import datetime, timedelta

class ForgotPasswordDialog(QDialog):
    def __init__(self, user_model, parent=None):
        super().__init__(parent)
        self.user_model = user_model
        self.reset_token = None
        self.user_email = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Reset Password")
        self.setModal(True)
        self.resize(400, 300)

        self.setStyleSheet("background-color: #f9fafb; color: black;")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Logo pic
        logo_path = "system_images/forgot_pass.png"

        logo = QLabel()
        pix = QPixmap(logo_path)
        logo.setPixmap(pix.scaledToHeight(100, Qt.TransformationMode.SmoothTransformation)) #scales img
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # Title
        title = QLabel("Reset Your Password") 
        title.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: black;") 
        layout.addWidget(title)
        
        # Step 1: Email input
        self.step1_widget = QWidget()
        step1_layout = QVBoxLayout()
        
        email_label = QLabel("Enter your email address:")
        email_label.setStyleSheet("color: #666; font-size: 14px;")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Your registered email")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
                color: black;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        
        send_btn = QPushButton("Send Reset Link")
        send_btn.setStyleSheet("""
            QPushButton {
                background: #e67e22;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #f9d162;
            }
        """)
        send_btn.clicked.connect(self.send_reset_link)
        
        step1_layout.addWidget(email_label)
        step1_layout.addWidget(self.email_input)
        step1_layout.addWidget(send_btn)
        self.step1_widget.setLayout(step1_layout)
        
        # Step 2: Token and new password
        self.step2_widget = QWidget()
        self.step2_widget.setVisible(False)
        step2_layout = QVBoxLayout()
        
        token_label = QLabel("Enter reset token:")
        token_label.setStyleSheet("color: black; font-size: 14px;")
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Check your email for the reset token")
        self.token_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
                color: black;
            }
        """)
        
        new_pass_label = QLabel("New password:")
        new_pass_label.setStyleSheet("color: black; font-size: 14px;")
        
        self.new_pass_input = QLineEdit()
        self.new_pass_input.setPlaceholderText("Enter new password")
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
                color: black;
            }
        """)
        
        confirm_pass_label = QLabel("Confirm new password:")
        confirm_pass_label.setStyleSheet("color: black; font-size: 14px;")
        
        self.confirm_pass_input = QLineEdit()
        self.confirm_pass_input.setPlaceholderText("Confirm new password")
        self.confirm_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pass_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
                color:black;
            }
        """)
        
        reset_btn = QPushButton("Reset Password")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #e67e22;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #f9d162;
            }
        """)
        reset_btn.clicked.connect(self.reset_password)
        
        step2_layout.addWidget(token_label)
        step2_layout.addWidget(self.token_input)
        step2_layout.addWidget(new_pass_label)
        step2_layout.addWidget(self.new_pass_input)
        step2_layout.addWidget(confirm_pass_label)
        step2_layout.addWidget(self.confirm_pass_input)
        step2_layout.addWidget(reset_btn)
        self.step2_widget.setLayout(step2_layout)
        
        layout.addWidget(self.step1_widget)
        layout.addWidget(self.step2_widget)
        self.setLayout(layout)
    
    def generate_reset_token(self):
        # Generate a secure random token
        return secrets.token_urlsafe(32)
    
    def send_reset_email(self, email, token):
        # Simulate sending reset email
        QMessageBox.information(
            self, 
            "Reset Token", 
            f'<font color="black">Reset token for {email}:<br><br>'
            f'<b>{token}</b><br><br>'
            'Please use this token to reset your password.</font>'
        )
    
    def send_reset_link(self):
        email = self.email_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Error", '<font color="black">Please enter your email address</font>')
            return
    
        try:
            # Check if user exists
            user = self.user_model.get_user_by_email(email)
            if not user:
                QMessageBox.warning(self, "Error", '<font color="black">No account found with this email address</font>')
                return
    
            # Generate reset token and expiry
            self.reset_token = self.generate_reset_token()
            expiry = datetime.now() + timedelta(hours=1)
    
            # Store token in database
            if self.user_model.set_reset_token(email, self.reset_token, expiry):
                # Send email
                self.send_reset_email(email, self.reset_token)
            
                # Store email for step 2 and show step 2
                self.user_email = email
                self.step1_widget.setVisible(False)
                self.step2_widget.setVisible(True)
                self.resize(400, 450)
            
                QMessageBox.information(self, "Success", '<font color="black">Please check your email for the reset token and enter it below.</font>')
            else:
                QMessageBox.warning(self, "Error", '<font color="black">Failed to generate reset token</font>')
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f'<font color="black">An error occurred: {str(e)}</font>')
    
    def reset_password(self):
        token = self.token_input.text().strip()
        new_password = self.new_pass_input.text().strip()
        confirm_password = self.confirm_pass_input.text().strip()
        
        if not token or not new_password or not confirm_password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters long")
            return
        
        try:
            # Verify the reset token is valid for this email
            if self.user_model.verify_reset_token(self.user_email, token):
                # Update the password
                if self.user_model.update_password(self.user_email, new_password):
                    QMessageBox.information(self, "Success", "Password reset successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to reset password")
            else:
                QMessageBox.warning(self, "Error", "Invalid or expired reset token")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")