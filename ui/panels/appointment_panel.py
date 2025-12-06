from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QTimeEdit, QTextEdit,
                             QMessageBox, QHeaderView, QDialog, QFormLayout,
                             QDialogButtonBox, QCalendarWidget)
from PyQt6.QtCore import QDateTime, Qt
from datetime import datetime, timedelta
from models.appointment_model import AppointmentModel
from models.user_model import UserModel

class AppointmentPanel(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.appointment_model = AppointmentModel(db)
        self.user_model = UserModel(db)
        self.init_ui()
        self.load_appointments()
        if user_role in ['admin', 'staff']:
            self.load_staff()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title = QLabel("Appointment Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        if self.user_role == 'customer':
            new_btn = QPushButton("Book Appointment")
            new_btn.setStyleSheet("""
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
            new_btn.clicked.connect(self.book_appointment)
            header_layout.addWidget(new_btn)
        else:
            new_btn = QPushButton("New Appointment")
            new_btn.setStyleSheet("""
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
            new_btn.clicked.connect(self.create_appointment)
            header_layout.addWidget(new_btn)
        
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Pending", "Approved", "Completed", "Cancelled"])
        self.status_combo.currentTextChanged.connect(self.filter_appointments)
        
        filter_layout.addWidget(self.status_combo)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        layout.addSpacing(10)
        
        # Appointments table
        self.appointments_table = QTableWidget()
        if self.user_role in ['admin', 'staff']:
            self.appointments_table.setColumnCount(7)
            self.appointments_table.setHorizontalHeaderLabels([
                "ID", "Customer", "Service", "Date & Time", "Staff", "Status", "Actions"
            ])
        else:
            self.appointments_table.setColumnCount(6)
            self.appointments_table.setHorizontalHeaderLabels([
                "ID", "Service", "Date & Time", "Staff", "Status", "Actions"
            ])
        
        self.appointments_table.setStyleSheet("""
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
        
        self.appointments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.appointments_table)
        
        self.setLayout(layout)
    
    def load_appointments(self):
        if self.user_role == 'customer':
            appointments = self.appointment_model.get_appointments_by_customer(1)  # Would use actual customer ID
        else:
            appointments = self.appointment_model.get_all_appointments()
        
        self.appointments_table.setRowCount(len(appointments))
        
        for row, appointment in enumerate(appointments):
            self.appointments_table.setItem(row, 0, QTableWidgetItem(str(appointment['id'])))
            
            col_offset = 0
            if self.user_role in ['admin', 'staff']:
                customer_name = f"{appointment['customer_first_name']} {appointment['customer_last_name']}"
                self.appointments_table.setItem(row, 1, QTableWidgetItem(customer_name))
                col_offset = 1
            
            self.appointments_table.setItem(row, 1 + col_offset, QTableWidgetItem(appointment['service_type']))
            
            # Format datetime
            appt_date = appointment['appointment_date']
            if isinstance(appt_date, str):
                appt_date = datetime.strptime(appt_date, '%Y-%m-%d %H:%M:%S')
            formatted_date = appt_date.strftime('%Y-%m-%d %I:%M %p')
            self.appointments_table.setItem(row, 2 + col_offset, QTableWidgetItem(formatted_date))
            
            staff_name = f"{appointment['staff_first_name']} {appointment['staff_last_name']}" if appointment['staff_first_name'] else "Not Assigned"
            self.appointments_table.setItem(row, 3 + col_offset, QTableWidgetItem(staff_name))
            
            status_item = QTableWidgetItem(appointment['status'])
            # Color code status
            if appointment['status'] == 'Pending':
                status_item.setBackground(Qt.GlobalColor.yellow)
            elif appointment['status'] == 'Approved':
                status_item.setBackground(Qt.GlobalColor.blue)
                status_item.setForeground(Qt.GlobalColor.white)
            elif appointment['status'] == 'Completed':
                status_item.setBackground(Qt.GlobalColor.green)
                status_item.setForeground(Qt.GlobalColor.white)
            elif appointment['status'] == 'Cancelled':
                status_item.setBackground(Qt.GlobalColor.red)
                status_item.setForeground(Qt.GlobalColor.white)
            
            self.appointments_table.setItem(row, 4 + col_offset, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            if self.user_role in ['admin', 'staff']:
                if appointment['status'] == 'Pending':
                    approve_btn = QPushButton("Approve")
                    approve_btn.setStyleSheet("""
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
                    approve_btn.clicked.connect(lambda checked, a=appointment: self.update_status(a['id'], 'Approved'))
                    actions_layout.addWidget(approve_btn)
                
                if appointment['status'] in ['Pending', 'Approved']:
                    complete_btn = QPushButton("Complete")
                    complete_btn.setStyleSheet("""
                        QPushButton {
                            background: #17a2b8;
                            color: white;
                            padding: 5px 10px;
                            border: none;
                            border-radius: 5px;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background: #138496;
                        }
                    """)
                    complete_btn.clicked.connect(lambda checked, a=appointment: self.update_status(a['id'], 'Completed'))
                    actions_layout.addWidget(complete_btn)
                
                cancel_btn = QPushButton("Cancel")
                cancel_btn.setStyleSheet("""
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
                cancel_btn.clicked.connect(lambda checked, a=appointment: self.update_status(a['id'], 'Cancelled'))
                actions_layout.addWidget(cancel_btn)
            
            else:  # Customer
                if appointment['status'] == 'Pending':
                    cancel_btn = QPushButton("Cancel")
                    cancel_btn.setStyleSheet("""
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
                    cancel_btn.clicked.connect(lambda checked, a=appointment: self.update_status(a['id'], 'Cancelled'))
                    actions_layout.addWidget(cancel_btn)
            
            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.appointments_table.setCellWidget(row, 5 + col_offset, actions_widget)
    
    def load_staff(self):
        self.staff_members = self.user_model.get_all_users('staff')
    
    def filter_appointments(self, status):
        if status == "All":
            for row in range(self.appointments_table.rowCount()):
                self.appointments_table.setRowHidden(row, False)
        else:
            for row in range(self.appointments_table.rowCount()):
                status_item = self.appointments_table.item(row, 4 if self.user_role in ['admin', 'staff'] else 3)
                if status_item and status_item.text() == status:
                    self.appointments_table.setRowHidden(row, False)
                else:
                    self.appointments_table.setRowHidden(row, True)
    
    def book_appointment(self):
        dialog = BookAppointmentDialog(self.appointment_model, self.user_id, self.staff_members)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_appointments()
    
    def create_appointment(self):
        dialog = CreateAppointmentDialog(self.appointment_model, self.staff_members)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_appointments()
    
    def update_status(self, appointment_id, new_status):
        if self.appointment_model.update_appointment_status(appointment_id, new_status):
            QMessageBox.information(self, "Success", f"Appointment status updated to {new_status}")
            self.load_appointments()
        else:
            QMessageBox.warning(self, "Error", "Failed to update appointment status")

class BookAppointmentDialog(QDialog):
    def __init__(self, appointment_model, customer_id, staff_members=None):
        super().__init__()
        self.appointment_model = appointment_model
        self.customer_id = customer_id
        self.staff_members = staff_members or []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Book Appointment")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QFormLayout()
        layout.setSpacing(15)
        
        self.service_combo = QComboBox()
        self.service_combo.addItems(["Grooming", "Vet Check-up", "Vaccination", "Spa", "Training"])
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDateTime.currentDateTime().date())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMinimumDate(QDateTime.currentDateTime().date())
        
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QDateTime.currentDateTime().time())
        self.time_edit.setTimeRange(QDateTime.currentDateTime().time(), QDateTime.currentDateTime().time().addSecs(3600*17))  # 9 AM to 5 PM
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        
        # Style inputs
        for widget in [self.service_combo, self.date_edit, self.time_edit]:
            widget.setStyleSheet("""
                QComboBox, QDateEdit, QTimeEdit {
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
            """)
        
        self.notes_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        layout.addRow("Service Type *:", self.service_combo)
        layout.addRow("Date *:", self.date_edit)
        layout.addRow("Time *:", self.time_edit)
        layout.addRow("Notes:", self.notes_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.book_appointment)
        button_box.rejected.connect(self.reject)
        
        layout.addRow(button_box)
        self.setLayout(layout)
    
    def book_appointment(self):
        service_type = self.service_combo.currentText()
        appointment_date = self.date_edit.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        notes = self.notes_input.toPlainText().strip()
        
        if not service_type:
            QMessageBox.warning(self, "Error", "Please select a service type")
            return
        
        appointment_data = {
            'customer_id': self.customer_id,
            'service_type': service_type,
            'appointment_date': appointment_date,
            'notes': notes
        }
        
        if self.appointment_model.create_appointment(appointment_data):
            QMessageBox.information(self, "Success", "Appointment booked successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to book appointment")

class CreateAppointmentDialog(QDialog):
    def __init__(self, appointment_model, staff_members):
        super().__init__()
        self.appointment_model = appointment_model
        self.staff_members = staff_members
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Create Appointment")
        self.setModal(True)
        self.resize(400, 400)
        
        layout = QFormLayout()
        layout.setSpacing(15)
        
        # Customer selection would be here in real implementation
        self.service_combo = QComboBox()
        self.service_combo.addItems(["Grooming", "Vet Check-up", "Vaccination", "Spa", "Training"])
        
        self.staff_combo = QComboBox()
        self.staff_combo.addItem("Not Assigned", None)
        for staff in self.staff_members:
            self.staff_combo.addItem(f"{staff['first_name']} {staff['last_name']}", staff['id'])
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDateTime.currentDateTime().date())
        self.date_edit.setCalendarPopup(True)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QDateTime.currentDateTime().time())
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        
        layout.addRow("Service Type *:", self.service_combo)
        layout.addRow("Staff:", self.staff_combo)
        layout.addRow("Date *:", self.date_edit)
        layout.addRow("Time *:", self.time_edit)
        layout.addRow("Notes:", self.notes_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.create_appointment)
        button_box.rejected.connect(self.reject)
        
        layout.addRow(button_box)
        self.setLayout(layout)
    
    def create_appointment(self):
        # Similar to book_appointment but with staff assignment
        # Implementation would be similar to BookAppointmentDialog
        pass