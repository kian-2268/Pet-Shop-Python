from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QTimeEdit, QTextEdit,
                             QMessageBox, QHeaderView, QDialog, QDialogButtonBox, 
                             QGroupBox, QScrollArea, QGridLayout)
from PyQt6.QtCore import QDateTime, Qt
from datetime import datetime
from models.appointment_model import AppointmentModel
from models.user_model import UserModel

class AppointmentPanel(QWidget):
    def __init__(self, db, user_role, user_id=None):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.user_id = user_id  # Store user_id if available
        self.appointment_model = AppointmentModel(db)
        self.user_model = UserModel(db)
        self.init_ui()
        self.load_appointments()
        if user_role in ['admin', 'staff']:
            self.load_staff()
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header 
        header_layout = QHBoxLayout()
        title = QLabel("Appointment Management")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        header_layout.addWidget(title)
        header_layout.addSpacing(10)
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
        layout.addSpacing(10)
        
        # Search/Filters 
        search_layout = QHBoxLayout()
        
        # Label with white background
        search_label = QLabel("Filter by Status:")
        search_label.setStyleSheet("""
            QLabel {    
                background-color: #f9fafb;
                color: black;
                padding: 5px 10px;
            }
        """)
        search_layout.addWidget(search_label)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Pending", "Approved", "Completed", "Cancelled"])
        self.status_combo.setStyleSheet("""
            QComboBox {
                color: black;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #555;
            }
        """)
        self.status_combo.currentTextChanged.connect(self.filter_appointments)
        
        search_layout.addWidget(self.status_combo)
        search_layout.addStretch()
        
        layout.addLayout(search_layout)
        layout.addSpacing(20)
        
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
        
        # Style the table
        self.appointments_table.setStyleSheet("""
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
        header = self.appointments_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        if self.user_role in ['admin', 'staff']:
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Customer
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Service
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Date & Time
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Staff
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Actions
        else:
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Service
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Date & Time
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Staff
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Status
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Actions
        
        layout.addWidget(self.appointments_table)
        
        self.setLayout(layout)
    
    def load_appointments(self):
        if self.user_role == 'customer' and self.user_id:
            appointments = self.appointment_model.get_appointments_by_customer(self.user_id)
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
                try:
                    appt_date = datetime.strptime(appt_date, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    appt_date = datetime.strptime(appt_date, '%Y-%m-%d')
            formatted_date = appt_date.strftime('%Y-%m-%d %I:%M %p')
            self.appointments_table.setItem(row, 2 + col_offset, QTableWidgetItem(formatted_date))
            
            staff_name = f"{appointment['staff_first_name']} {appointment['staff_last_name']}" if appointment['staff_first_name'] else "Not Assigned"
            self.appointments_table.setItem(row, 3 + col_offset, QTableWidgetItem(staff_name))
            
            # Status with color coding 
            status_item = QTableWidgetItem(appointment['status'])
            if appointment['status'] == 'Pending':
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            elif appointment['status'] == 'Approved':
                status_item.setForeground(Qt.GlobalColor.darkBlue)
            elif appointment['status'] == 'Completed':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif appointment['status'] == 'Cancelled':
                status_item.setForeground(Qt.GlobalColor.darkRed)
            
            self.appointments_table.setItem(row, 4 + col_offset, status_item)
            
            # Actions 
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background-color: white;")
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            if self.user_role in ['admin', 'staff']:
                if appointment['status'] == 'Pending':
                    approve_btn = QPushButton("Approve")
                    approve_btn.setMinimumHeight(20)
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
                    complete_btn.setMinimumHeight(20)
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
                cancel_btn.setMinimumHeight(20)
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
                    cancel_btn.setMinimumHeight(20)
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
        status_col = 5 if self.user_role in ['admin', 'staff'] else 4
        
        if status == "All":
            for row in range(self.appointments_table.rowCount()):
                self.appointments_table.setRowHidden(row, False)
        else:
            for row in range(self.appointments_table.rowCount()):
                status_item = self.appointments_table.item(row, status_col)
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
        # Confirmation dialog 
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"Confirm Status Update")
        msg_box.setText(f"Are you sure you want to change the appointment status to '{new_status}'?")
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
            if self.appointment_model.update_appointment_status(appointment_id, new_status):
                # Success message 
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText(f"Appointment status updated to {new_status}")
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
                self.load_appointments()
            else:
                # Error message 
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Error")
                error_msg.setText("Failed to update appointment status")
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
        self.setStyleSheet("background-color: white; color: black;")
        self.resize(600, 500)  
        
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
        
        # Appointment Information Group 
        appointment_group = QGroupBox("Appointment Information")
        appointment_group.setStyleSheet("""
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
        appointment_layout = QGridLayout()
        appointment_layout.setHorizontalSpacing(20)
        appointment_layout.setVerticalSpacing(10)
        
        # Service Type 
        appointment_layout.addWidget(QLabel("Service Type *:"), 0, 0)
        self.service_combo = QComboBox()
        self.service_combo.addItems(["Grooming", "Vet Check-up", "Vaccination", "Spa", "Training"])
        self.service_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        appointment_layout.addWidget(self.service_combo, 0, 1, 1, 3)
        
        # Date and Time
        appointment_layout.addWidget(QLabel("Date *:"), 1, 0)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDateTime.currentDateTime().date())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMinimumDate(QDateTime.currentDateTime().date())
        self.date_edit.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        appointment_layout.addWidget(self.date_edit, 1, 1)
        
        appointment_layout.addWidget(QLabel("Time *:"), 1, 2)
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QDateTime.currentDateTime().time())
        self.time_edit.setTimeRange(QDateTime.currentDateTime().time(), QDateTime.currentDateTime().time().addSecs(3600*17))
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        appointment_layout.addWidget(self.time_edit, 1, 3)
        
        # Notes 
        appointment_layout.addWidget(QLabel("Notes:"), 2, 0)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        appointment_layout.addWidget(self.notes_input, 2, 1, 1, 3)
        
        appointment_group.setLayout(appointment_layout)
        container_layout.addWidget(appointment_group)
        
        container_widget.setLayout(container_layout)
        scroll_area.setWidget(container_widget)
        main_layout.addWidget(scroll_area)
        
        # Buttons 
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.book_appointment)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
    
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
        self.setStyleSheet("background-color: white; color: black;")
        self.resize(600, 500) 
        
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
        
        # Appointment Information Group 
        appointment_group = QGroupBox("Appointment Information")
        appointment_group.setStyleSheet("""
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
        appointment_layout = QGridLayout()
        appointment_layout.setHorizontalSpacing(20)
        appointment_layout.setVerticalSpacing(10)
        
        # Service Type 
        appointment_layout.addWidget(QLabel("Service Type *:"), 0, 0)
        self.service_combo = QComboBox()
        self.service_combo.addItems(["Grooming", "Vet Check-up", "Vaccination", "Spa", "Training"])
        self.service_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        appointment_layout.addWidget(self.service_combo, 0, 1, 1, 3)
        
        # Staff
        appointment_layout.addWidget(QLabel("Staff:"), 1, 0)
        self.staff_combo = QComboBox()
        self.staff_combo.addItem("Not Assigned", None)
        for staff in self.staff_members:
            self.staff_combo.addItem(f"{staff['first_name']} {staff['last_name']}", staff['id'])
        self.staff_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        appointment_layout.addWidget(self.staff_combo, 1, 1, 1, 3)
        
        # Date and Time
        appointment_layout.addWidget(QLabel("Date *:"), 2, 0)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDateTime.currentDateTime().date())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        appointment_layout.addWidget(self.date_edit, 2, 1)
        
        appointment_layout.addWidget(QLabel("Time *:"), 2, 2)
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QDateTime.currentDateTime().time())
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        appointment_layout.addWidget(self.time_edit, 2, 3)
        
        # Notes
        appointment_layout.addWidget(QLabel("Notes:"), 3, 0)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        appointment_layout.addWidget(self.notes_input, 3, 1, 1, 3)
        
        appointment_group.setLayout(appointment_layout)
        container_layout.addWidget(appointment_group)
        
        container_widget.setLayout(container_layout)
        scroll_area.setWidget(container_widget)
        main_layout.addWidget(scroll_area)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.create_appointment)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
    
    def create_appointment(self):
        service_type = self.service_combo.currentText()
        staff_id = self.staff_combo.currentData()
        appointment_date = self.date_edit.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        notes = self.notes_input.toPlainText().strip()
        
        if not service_type:
            QMessageBox.warning(self, "Error", "Please select a service type")
            return
        
        appointment_data = {
            'service_type': service_type,
            'appointment_date': appointment_date,
            'notes': notes,
            'staff_id': staff_id
        }
        
        appointment_data['customer_id'] = 1  
        
        if self.appointment_model.create_appointment(appointment_data):
            QMessageBox.information(self, "Success", "Appointment created successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to create appointment")
