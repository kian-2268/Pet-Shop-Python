from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QMessageBox, QGroupBox, QFormLayout, QTextEdit
)
from PyQt6.QtCore import QTimer
from models.user_model import UserModel

class ProfilePanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.user_model = UserModel(db)
        self.init_ui()
        QTimer.singleShot(0, self.load_user_data)
    
    def init_ui(self):
        self.setStyleSheet("background-color: white; color; black")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("My Profile")
        title.setStyleSheet("""
            background-color: #f9fafb;
            font-size: 25px;
            font-weight: bold;
            color: black;
        """)
        layout.addWidget(title)
        
        # Personal information group
        personal_group = QGroupBox("Personal Information")
        personal_group.setStyleSheet(self.get_groupbox_style())
        
        personal_layout = QFormLayout()
        personal_layout.setSpacing(15)
        
        # Create styled labels for form
        first_name_label = self.create_form_label("First Name *:")
        last_name_label = self.create_form_label("Last Name *:")
        email_label = self.create_form_label("Email *:")
        phone_label = self.create_form_label("Phone:")
        address_label = self.create_form_label("Address:")
        
        # Create input fields
        self.first_name_input = self.create_line_edit()
        self.last_name_input = self.create_line_edit()
        self.email_input = self.create_line_edit()
        self.phone_input = self.create_line_edit()
        self.address_input = self.create_text_edit()

        # Add fields to layout with styled labels
        personal_layout.addRow(first_name_label, self.first_name_input)
        personal_layout.addRow(last_name_label, self.last_name_input)
        personal_layout.addRow(email_label, self.email_input)
        personal_layout.addRow(phone_label, self.phone_input)
        personal_layout.addRow(address_label, self.address_input)
        
        personal_group.setLayout(personal_layout)
        layout.addWidget(personal_group)
        
        # Password change group
        password_group = QGroupBox("Change Password")
        password_group.setStyleSheet(self.get_groupbox_style())
        
        password_layout = QFormLayout()
        password_layout.setSpacing(15)
        
        # Create styled labels for password form
        current_password_label = self.create_form_label("Current Password:")
        new_password_label = self.create_form_label("New Password:")
        confirm_password_label = self.create_form_label("Confirm Password:")
        
        # Create password fields
        self.current_password_input = self.create_password_edit()
        self.new_password_input = self.create_password_edit()
        self.confirm_password_input = self.create_password_edit()

        password_layout.addRow(current_password_label, self.current_password_input)
        password_layout.addRow(new_password_label, self.new_password_input)
        password_layout.addRow(confirm_password_label, self.confirm_password_input)
        
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        save_profile_btn = self.create_button("Save Profile", "#5ab9ea", "#78d1ff")
        save_profile_btn.clicked.connect(self.save_profile)
        
        change_password_btn = self.create_button("Change Password", "#e67e22", "#e67e22")
        change_password_btn.clicked.connect(self.change_password)
        
        buttons_layout.addWidget(save_profile_btn)
        buttons_layout.addWidget(change_password_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def create_form_label(self, text):
        # Create a form label with black text
        label = QLabel(text)
        label.setStyleSheet("color: black; font-size: 14px;")
        return label
    
    def show_styled_message(self, title, message, icon_type=QMessageBox.Icon.Information):
        # Show a styled message box with white background and black text
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon_type)
    
        # Apply styles
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: black;
                background-color: white;
            }
            QMessageBox QPushButton {
                background-color: #5ab9ea;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #78d1ff;
            }
        """)
    
        return msg_box.exec()
    
    def get_groupbox_style(self):
        return """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e1e1e1;
                border-radius: 8px;
                margin-top: 10px;
                background: white;
                color: black;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #f9fafb;
                color: black;
            }
        """
    
    def create_line_edit(self):
        line_edit = QLineEdit()
        line_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
                color: black;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        return line_edit
    
    def create_text_edit(self):
        text_edit = QTextEdit()
        text_edit.setMaximumHeight(80)
        text_edit.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
                color: black;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        return text_edit
    
    def create_password_edit(self):
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
                color: black;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        return password_edit
    
    def create_button(self, text, color, hover_color):
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                min-width: 150px;
            }}
            QPushButton:hover {{
                background: {hover_color};
            }}
        """)
        return button
    
    def load_user_data(self):
        try:
            user = self.user_model.get_user_by_id(self.user_id)
            if user:
                self.first_name_input.setText(user.get('first_name', ''))
                self.last_name_input.setText(user.get('last_name', ''))
                self.email_input.setText(user.get('email', ''))
                self.phone_input.setText(user.get('phone', ''))
                self.address_input.setText(user.get('address', ''))
        except Exception as e:
            self.show_styled_message("Error", f"Failed to load user data: {str(e)}", QMessageBox.Icon.Critical)

    def save_profile(self):
        # Save profile information
        # Get data from input fields
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.toPlainText().strip()
        
        # Basic validation
        if not first_name or not last_name:
            self.show_styled_message("Validation Error", "First name and last name are required!", 
                         QMessageBox.Icon.Warning)
            return
        
        if not email:
            self.show_styled_message("Validation Error", "Email is required!", QMessageBox.Icon.Warning)
            return
        
        # Prepare update data
        update_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'address': address
        }
        
        try:
            success = self.user_model.update_user(self.user_id, update_data)
            
            if success:
                self.show_styled_message("Success", "Profile updated successfully!")
            else:
                self.show_styled_message("Error", "Failed to update profile!", QMessageBox.Icon.Warning)
                    
        except Exception as e:
            self.show_styled_message("Error", 
                               f"An error occurred: {str(e)}", QMessageBox.Icon.Critical)
    
    def change_password(self):
        """Change user password"""
        current_password = self.current_password_input.text().strip()
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        # Validation
        if not current_password or not new_password or not confirm_password:
            self.show_styled_message("Error", "Please fill in all password fields", QMessageBox.Icon.Warning)
            return
        
        if new_password != confirm_password:
            self.show_styled_message("Error", "New passwords do not match", QMessageBox.Icon.Warning)
            return
        
        if len(new_password) < 6:
            self.show_styled_message("Error", "Password must be at least 6 characters long", QMessageBox.Icon.Warning)
            return
        
        try:
            # Verify current password
            user = self.user_model.get_user_by_id(self.user_id)
            
            if not user or user.get('password') != current_password:
                self.show_styled_message("Error", "Current password is incorrect", QMessageBox.Icon.Warning)
                return
            
            # Update password
            if self.user_model.update_password(self.user_id, new_password):
                if hasattr(self.user_model, 'close'):
                    self.user_model.close()
                self.user_model = UserModel(self.db)
                self.show_styled_message("Success", 
                                      "Password changed successfully!")
                
                # Clear password fields
                self.current_password_input.clear()
                self.new_password_input.clear()
                self.confirm_password_input.clear()
            else:
                self.show_styled_message("Error", 
                                   "Failed to update password in database!", QMessageBox.Icon.Critical)
                
        except Exception as e:
            self.show_styled_message("Error", 
                               f"Failed to change password: {str(e)}", QMessageBox.Icon.Critical)
