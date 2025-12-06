from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QDialogButtonBox, QComboBox)
from PyQt6.QtCore import Qt
from datetime import datetime
from models.user_model import UserModel

class StaffManagementPanel(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_model = UserModel(db)
        self.init_ui()
        self.load_staff()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and controls
        header_layout = QHBoxLayout()
        title = QLabel("Staff Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_btn = QPushButton("Add Staff")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        add_btn.clicked.connect(self.add_staff)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search staff...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        self.search_input.textChanged.connect(self.search_staff)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        layout.addSpacing(10)
        
        # Staff table
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(8)
        self.staff_table.setHorizontalHeaderLabels([
            "ID", "Username", "Name", "Email", "Phone", "Status", "Joined", "Actions"
        ])
        
        self.staff_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e1e1e1;
                border-radius: 8px;
                background: white;
            }
            QHeaderView::section {
                background: #f8f9fa;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        self.staff_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
            
            status_item = QTableWidgetItem("Active" if user['is_active'] else "Inactive")
            if user['is_active']:
                status_item.setBackground(Qt.GlobalColor.green)
                status_item.setForeground(Qt.GlobalColor.white)
            else:
                status_item.setBackground(Qt.GlobalColor.red)
                status_item.setForeground(Qt.GlobalColor.white)
            self.staff_table.setItem(row, 5, status_item)
            
            join_date = user['created_at'].strftime('%Y-%m-%d') if isinstance(user['created_at'], datetime) else user['created_at']
            self.staff_table.setItem(row, 6, QTableWidgetItem(join_date))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #007bff;
                    color: white;
                    padding: 5px 10px;
                    border: none;
                    border-radius: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #0056b3;
                }
            """)
            edit_btn.clicked.connect(lambda checked, u=user: self.edit_staff(u))
            
            if user['is_active']:
                deactivate_btn = QPushButton("Deactivate")
                deactivate_btn.setStyleSheet("""
                    QPushButton {
                        background: #ffc107;
                        color: black;
                        padding: 5px 10px;
                        border: none;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background: #e0a800;
                    }
                """)
                deactivate_btn.clicked.connect(lambda checked, u=user: self.toggle_staff_status(u['id'], False))
            else:
                activate_btn = QPushButton("Activate")
                activate_btn.setStyleSheet("""
                    QPushButton {
                        background: #28a745;
                        color: white;
                        padding: 5px 10px;
                        border: none;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background: #218838;
                    }
                """)
                activate_btn.clicked.connect(lambda checked, u=user: self.toggle_staff_status(u['id'], True))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #dc3545;
                    color: white;
                    padding: 5px 10px;
                    border: none;
                    border-radius: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #c82333;
                }
            """)
            delete_btn.clicked.connect(lambda checked, u=user: self.delete_staff(u['id']))
            
            actions_layout.addWidget(edit_btn)
            if user['is_active']:
                actions_layout.addWidget(deactivate_btn)
            else:
                actions_layout.addWidget(activate_btn)
            actions_layout.addWidget(delete_btn)
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
        reply = QMessageBox.question(self, f"Confirm {action.title()}", 
                                   f"Are you sure you want to {action} this staff member?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if activate:
                # Reactivate staff
                query = "UPDATE users SET is_active = TRUE WHERE id = %s"
            else:
                # Deactivate staff
                query = "UPDATE users SET is_active = FALSE WHERE id = %s"
            
            if self.db.execute_query(query, (staff_id,)):
                QMessageBox.information(self, "Success", f"Staff member {action}d successfully")
                self.load_staff()
            else:
                QMessageBox.warning(self, "Error", f"Failed to {action} staff member")
    
    def delete_staff(self, staff_id):
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   "Are you sure you want to delete this staff member?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.user_model.deactivate_user(staff_id):
                QMessageBox.information(self, "Success", "Staff member deleted successfully")
                self.load_staff()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete staff member")

class AddEditStaffDialog(QDialog):
    def __init__(self, user_model, staff=None):
        super().__init__()
        self.user_model = user_model
        self.staff = staff
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Add Staff" if not self.staff else "Edit Staff")
        self.setModal(True)
        self.resize(400, 500)
        
        layout = QFormLayout()
        layout.setSpacing(15)
        
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.username_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Leave blank to keep current password" if self.staff else "")
        
        # Style inputs
        for widget in [self.first_name_input, self.last_name_input, self.username_input,
                      self.email_input, self.phone_input, self.address_input, self.password_input]:
            widget.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
            """)
        
        layout.addRow("First Name *:", self.first_name_input)
        layout.addRow("Last Name *:", self.last_name_input)
        layout.addRow("Username *:", self.username_input)
        layout.addRow("Email *:", self.email_input)
        layout.addRow("Phone:", self.phone_input)
        layout.addRow("Address:", self.address_input)
        layout.addRow("Password" + ("" if self.staff else " *:"), self.password_input)
        
        # Load staff data if editing
        if self.staff:
            self.load_staff_data()
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_staff)
        button_box.rejected.connect(self.reject)
        
        layout.addRow(button_box)
        self.setLayout(layout)
    
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
        
        if self.staff:
            # Update existing staff
            user_data = (
                self.email_input.text().strip(),
                self.first_name_input.text().strip(),
                self.last_name_input.text().strip(),
                self.phone_input.text().strip(),
                self.address_input.text().strip(),
                self.staff['id']
            )
            
            if self.user_model.update_user(self.staff['id'], user_data):
                # Update password if provided
                if self.password_input.text().strip():
                    query = "UPDATE users SET password = %s WHERE id = %s"
                    self.user_model.db.execute_query(query, (self.password_input.text().strip(), self.staff['id']))
                
                QMessageBox.information(self, "Success", "Staff member updated successfully")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to update staff member")
        else:
            # Add new staff
            user_data = (
                self.username_input.text().strip(),
                self.password_input.text().strip(),
                self.email_input.text().strip(),
                self.first_name_input.text().strip(),
                self.last_name_input.text().strip(),
                self.phone_input.text().strip(),
                self.address_input.text().strip(),
                'staff'
            )
            
            if self.user_model.create_user(user_data):
                QMessageBox.information(self, "Success", "Staff member added successfully")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to add staff member")