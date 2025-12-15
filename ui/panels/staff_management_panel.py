from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QMessageBox, QHeaderView, QDialog,
                             QDialogButtonBox, QGroupBox, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt
from datetime import datetime
from models.user_model import UserModel

class AddEditStaffDialog(QDialog):
    def __init__(self, user_model, staff=None):
        super().__init__()
        self.user_model = user_model
        self.staff = staff
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Add Staff" if not self.staff else "Edit Staff")
        self.setModal(True)
        self.resize(600, 500)
        self.setStyleSheet("background-color: white; color: black;")
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create scroll area for the form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                background: #f1f1f1;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8a8a8;
            }
        """)
        
        # Create container widget for the form
        container_widget = QWidget()
        container_widget.setStyleSheet("background-color: white;")
        container_layout = QVBoxLayout()
        container_layout.setSpacing(20)
        
        # Basic Information Group
        basic_group = QGroupBox("Basic Information")
        basic_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: black;
            }
        """)
        basic_layout = QGridLayout()
        basic_layout.setHorizontalSpacing(20)
        basic_layout.setVerticalSpacing(10)
        
        # Row 0
        basic_layout.addWidget(QLabel("First Name *:"), 0, 0)
        self.first_name_input = QLineEdit()
        self.first_name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.first_name_input, 0, 1)
        
        basic_layout.addWidget(QLabel("Last Name *:"), 0, 2)
        self.last_name_input = QLineEdit()
        self.last_name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.last_name_input, 0, 3)
        
        # Row 1
        basic_layout.addWidget(QLabel("Username *:"), 1, 0)
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.username_input, 1, 1)
        
        basic_layout.addWidget(QLabel("Email *:"), 1, 2)
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.email_input, 1, 3)
        
        # Row 2
        basic_layout.addWidget(QLabel("Phone:"), 2, 0)
        self.phone_input = QLineEdit()
        self.phone_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.phone_input, 2, 1)
        
        basic_layout.addWidget(QLabel("Address:"), 2, 2)
        self.address_input = QLineEdit()
        self.address_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.address_input, 2, 3)
        
        basic_group.setLayout(basic_layout)
        container_layout.addWidget(basic_group)
        
        # Password Group
        password_group = QGroupBox("Account Information")
        password_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: black;
            }
        """)
        password_layout = QGridLayout()
        password_layout.setHorizontalSpacing(20)
        password_layout.setVerticalSpacing(10)
        
        password_layout.addWidget(QLabel("Password" + ("" if self.staff else " *:")), 0, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Leave blank to keep current password" if self.staff else "")
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        password_layout.addWidget(self.password_input, 0, 1, 1, 3)
        
        password_group.setLayout(password_layout)
        container_layout.addWidget(password_group)
        
        container_widget.setLayout(container_layout)
        scroll_area.setWidget(container_widget)
        main_layout.addWidget(scroll_area)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_staff)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
        
        # Load staff data if editing
        if self.staff:
            self.load_staff_data()
    
    def load_staff_data(self):
        self.first_name_input.setText(self.staff['first_name'])
        self.last_name_input.setText(self.staff['last_name'])
        self.username_input.setText(self.staff['username'])
        self.email_input.setText(self.staff['email'])
        self.phone_input.setText(self.staff['phone'] or '')
        self.address_input.setText(self.staff['address'] or '')
    
    def save_staff(self):
        # Validate required fields
        required_fields = {
            'First Name': self.first_name_input.text().strip(),
            'Last Name': self.last_name_input.text().strip(),
            'Username': self.username_input.text().strip(),
            'Email': self.email_input.text().strip()
        }
    
        if not self.staff:
            required_fields['Password'] = self.password_input.text().strip()
    
        for field, value in required_fields.items():
            if not value:
                QMessageBox.warning(self, "Error", f"{field} is required")
                return
    
        try:
            if self.staff:
                # Prepare user data as a DICTIONARY (not tuple)
                user_data = {
                    'first_name': self.first_name_input.text().strip(),
                    'last_name': self.last_name_input.text().strip(),
                    'email': self.email_input.text().strip(),
                    'phone': self.phone_input.text().strip(),
                    'address': self.address_input.text().strip(),
                    'username': self.username_input.text().strip()
                }
            
                # Update existing staff
                if self.user_model.update_user(self.staff['id'], user_data):
                    # Update password if provided
                    if self.password_input.text().strip():
                        self.user_model.update_password(self.staff['id'], self.password_input.text().strip())
                
                    QMessageBox.information(self, "Success", "Staff member updated successfully")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update staff member")
            else:
                # Add new staff - prepare user data as a dictionary
                user_data = {
                    'username': self.username_input.text().strip(),
                    'password': self.password_input.text().strip(),
                    'email': self.email_input.text().strip(),
                    'first_name': self.first_name_input.text().strip(),
                    'last_name': self.last_name_input.text().strip(),
                    'phone': self.phone_input.text().strip() or None,
                    'address': self.address_input.text().strip() or None,
                    'role': 'staff',
                    'is_active': 1
                }
            
                user_id = self.user_model.create_user(user_data)
                if user_id:
                    QMessageBox.information(self, "Success", "Staff member added successfully")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", 
                        "Failed to add staff member. Possible reasons:\n"
                        "1. Username already exists\n"
                        "2. Email already exists\n"
                        "3. Database connection issue\n"
                        "4. Database schema mismatch")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

class StaffManagementPanel(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_model = UserModel(db)
        self.init_ui()
        self.load_staff()
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Staff Management")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        header_layout.addWidget(title)
        header_layout.addSpacing(10)
        header_layout.addStretch()
        
        add_btn = QPushButton("Add Staff")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        add_btn.clicked.connect(self.add_staff)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Search
        search_layout = QHBoxLayout()
        
        # Label with white background
        search_label = QLabel("Search:")
        search_label.setStyleSheet("""
            QLabel {    
                background-color: #f9fafb;
                color: black;
                padding: 5px 10px;
            }
        """)
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, username, email...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                color: black;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        self.search_input.textChanged.connect(self.search_staff)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        
        layout.addLayout(search_layout)
        layout.addSpacing(20)
        
        # Staff table
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(8)
        self.staff_table.setHorizontalHeaderLabels([
            "ID", "Username", "Name", "Email", "Phone", "Status", "Joined", "Actions"
        ])
        
        # Style the table
        self.staff_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e1e1e1;
                border-radius: 8px;
                background: white;
                color: black;
            }
            QHeaderView::section {
                background: #f8f9fa;
                padding: 10px;
                border: none;
                font-weight: bold;
                color: black;
            }
        """)
        
        # Set column resize modes
        header = self.staff_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Username
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Phone
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Joined
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Actions
        
        layout.addWidget(self.staff_table)
        
        self.setLayout(layout)
    
    def load_staff(self):
        staff = self.user_model.get_all_users('staff')
        self.staff_table.setRowCount(len(staff))
        
        for row, user in enumerate(staff):
            self.staff_table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
            self.staff_table.setItem(row, 1, QTableWidgetItem(user['username']))
            self.staff_table.setItem(row, 2, QTableWidgetItem(f"{user['first_name']} {user['last_name']}"))
            self.staff_table.setItem(row, 3, QTableWidgetItem(user['email']))
            self.staff_table.setItem(row, 4, QTableWidgetItem(user['phone'] or 'N/A'))
            
            # Check if is_active is 1 (True) or 0 (False)
            is_active = bool(user['is_active']) if isinstance(user['is_active'], (int, float)) else user['is_active']
            
            # Status with color coding
            status_item = QTableWidgetItem("Active" if is_active else "Inactive")
            if is_active:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                status_item.setForeground(Qt.GlobalColor.darkRed)
            self.staff_table.setItem(row, 5, status_item)
            
            join_date = user['created_at'].strftime('%Y-%m-%d') if isinstance(user['created_at'], datetime) else user['created_at']
            self.staff_table.setItem(row, 6, QTableWidgetItem(join_date))
            
            # Actions
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background-color: white;")
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setMinimumHeight(20)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #3498db;
                    color: white;
                    padding: 5px 10px;
                    border: none;
                    border-radius: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, u=user: self.edit_staff(u))
            
            if is_active:
                deactivate_btn = QPushButton("Deactivate")
                deactivate_btn.setMinimumHeight(20)
                deactivate_btn.setStyleSheet("""
                    QPushButton {
                        background: #f39c12;
                        color: white;
                        padding: 5px 10px;
                        border: none;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background: #e67e22;
                    }
                """)
                deactivate_btn.clicked.connect(lambda checked, u=user: self.toggle_staff_status(u['id'], False))
                actions_layout.addWidget(deactivate_btn)
            else:
                activate_btn = QPushButton("Activate")
                activate_btn.setMinimumHeight(20)
                activate_btn.setStyleSheet("""
                    QPushButton {
                        background: #2ecc71;
                        color: white;
                        padding: 5px 10px;
                        border: none;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background: #27ae60;
                    }
                """)
                activate_btn.clicked.connect(lambda checked, u=user: self.toggle_staff_status(u['id'], True))
                actions_layout.addWidget(activate_btn)
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addStretch()
            
            actions_widget.setLayout(actions_layout)
            self.staff_table.setCellWidget(row, 7, actions_widget)
    
    def search_staff(self):
        search_text = self.search_input.text().lower()
        for row in range(self.staff_table.rowCount()):
            match = False
            for col in range(4):  # Check ID, Username, Name, Email
                item = self.staff_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.staff_table.setRowHidden(row, not match)
    
    def add_staff(self):
        dialog = AddEditStaffDialog(self.user_model)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_staff()
    
    def edit_staff(self, staff):
        dialog = AddEditStaffDialog(self.user_model, staff)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_staff()
    
    def toggle_staff_status(self, staff_id, activate):
        action = "activate" if activate else "deactivate"
        
        # Question dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"Confirm {action.title()}")
        msg_box.setText(f"Are you sure you want to {action} this staff member?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

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
            QMessageBox QPushButton:last-child {
                background-color: #95a5a6;
            }
            QMessageBox QPushButton:last-child:hover {
                background-color: #7f8c8d;
            }
        """)

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            # Use the UserModel method
            if self.user_model.toggle_user_status(staff_id, activate):
                # Success message
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText(f"Staff member {action}d successfully")
                success_msg.setIcon(QMessageBox.Icon.Information)
                success_msg.setStyleSheet("""
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
                success_msg.exec()
                self.load_staff()
            else:
                # Error message
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Error")
                error_msg.setText(f"Failed to {action} staff member")
                error_msg.setIcon(QMessageBox.Icon.Warning)
                error_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: white;
                    }
                    QMessageBox QLabel {
                        color: black;
                        background-color: white;
                    }
                    QMessageBox QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        padding: 8px 15px;
                        border: none;
                        border-radius: 5px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                error_msg.exec()
