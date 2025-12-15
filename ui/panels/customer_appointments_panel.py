from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QTimeEdit, QTextEdit,
                             QMessageBox, QHeaderView, QDialog, QFormLayout,
                             QDialogButtonBox, QGroupBox)
from PyQt6.QtCore import QDateTime, Qt, QTimer
from datetime import datetime
from models.appointment_model import AppointmentModel
from models.user_model import UserModel

class CustomerAppointmentsPanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.appointment_model = AppointmentModel(db)
        self.user_model = UserModel(db)
        self.init_ui()
        QTimer.singleShot(0, self.load_appointments) 
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("My Appointments")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        header_layout.addWidget(title)
        header_layout.addSpacing(10)
        header_layout.addStretch()
        
        new_btn = QPushButton("Book New Appointment")
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
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Filters
        filter_layout = QHBoxLayout()

        # Label with white background
        status_label = QLabel("Status:")
        status_label.setStyleSheet("""
            QLabel {    
                background-color: #f9fafb;
                color: black;
                padding: 5px 10px;
            }
        """)
        filter_layout.addWidget(status_label)

        # Combo box with white background
        self.status_combo = QComboBox()
        self.status_combo.setStyleSheet("""
            QComboBox {
                color: black;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
            }
        """)
        self.status_combo.addItems(["All", "Pending", "Approved", "Completed", "Cancelled"])
        self.status_combo.currentTextChanged.connect(self.filter_appointments)
        filter_layout.addWidget(self.status_combo)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        layout.addSpacing(10)
        
        # Appointments table
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(6)
        self.appointments_table.setHorizontalHeaderLabels([
            "ID", "Service", "Date & Time", "Staff", "Status", "Actions"
        ])
        
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
        
        self.appointments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.appointments_table)
        
        self.setLayout(layout)
    
    def load_appointments(self):
        appointments = self.appointment_model.get_appointments_by_customer(self.user_id)
        self.appointments_table.setRowCount(len(appointments))
        
        for row, appointment in enumerate(appointments):
            self.appointments_table.setItem(row, 0, QTableWidgetItem(str(appointment['id'])))
            self.appointments_table.setItem(row, 1, QTableWidgetItem(appointment['service_type']))
            
            # Format datetime
            appt_date = appointment['appointment_date']
            if isinstance(appt_date, str):
                appt_date = datetime.strptime(appt_date, '%Y-%m-%d %H:%M:%S')
            formatted_date = appt_date.strftime('%Y-%m-%d %I:%M %p')
            self.appointments_table.setItem(row, 2, QTableWidgetItem(formatted_date))
            
            staff_name = f"{appointment['staff_first_name']} {appointment['staff_last_name']}" if appointment['staff_first_name'] else "Not Assigned"
            self.appointments_table.setItem(row, 3, QTableWidgetItem(staff_name))
            
            status_item = QTableWidgetItem(appointment['status'])
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
            self.appointments_table.setItem(row, 4, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background-color: white;")
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.addStretch()

            view_btn = QPushButton("View Details")
            view_btn.setMinimumHeight(20)
            view_btn.setStyleSheet("""
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
            view_btn.clicked.connect(lambda checked, a=appointment: self.view_appointment_details(a))
            actions_layout.addWidget(view_btn)
            
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
                cancel_btn.clicked.connect(lambda checked, a=appointment: self.cancel_appointment(a['id']))
                actions_layout.addWidget(cancel_btn)
            # For cancelled status, show a disabled button or message
            elif appointment['status'] == 'Cancelled':
                cancelled_label = QLabel("Cancelled")
                cancelled_label.setMinimumHeight(20)
                cancelled_label.setStyleSheet("""
                    QLabel {
                        color: #666;
                        font-style: italic;
                        padding: 5px 10px;
                    }
                """)
                actions_layout.addWidget(cancelled_label)
            
            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.appointments_table.setCellWidget(row, 5, actions_widget)
    
    def filter_appointments(self, status):
        if status == "All":
            for row in range(self.appointments_table.rowCount()):
                self.appointments_table.setRowHidden(row, False)
        else:
            for row in range(self.appointments_table.rowCount()):
                status_item = self.appointments_table.item(row, 4)
                if status_item and status_item.text() == status:
                    self.appointments_table.setRowHidden(row, False)
                else:
                    self.appointments_table.setRowHidden(row, True)
    
    def book_appointment(self):
        dialog = BookAppointmentDialog(self.appointment_model, self.user_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_appointments()
    
    def cancel_appointment(self, appointment_id):
        # Question dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Cancel Appointment")
        msg_box.setText("Are you sure you want to cancel this appointment?")
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
            if self.appointment_model.update_appointment_status(appointment_id, 'Cancelled'):
                # Success message
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText("Appointment cancelled successfully")
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
                error_msg.setText("Failed to cancel appointment")
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
    
    def view_appointment_details(self, appointment):
        dialog = CustomerAppointmentDetailsDialog(appointment)
        dialog.exec()

class BookAppointmentDialog(QDialog):
    def __init__(self, appointment_model, customer_id):
        super().__init__()
        self.appointment_model = appointment_model
        self.customer_id = customer_id
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Book Appointment")
        self.setModal(True)
        self.resize(500, 400)
        self.setStyleSheet("background-color: white; color:black;")
        
        layout = QFormLayout()
        layout.setSpacing(15)
        
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
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Any special requirements or notes...")
        self.notes_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
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
        
        # Prepare appointment data with explicit staff_id as None
        appointment_data = {
            'customer_id': self.customer_id,
            'staff_id': None,  # Explicitly set to None for customer bookings
            'service_type': service_type,
            'appointment_date': appointment_date,
            'notes': notes if notes else ''
        }
        
        try:
            # Convert string to datetime for availability check
            from datetime import datetime
            appt_datetime = datetime.strptime(appointment_date, '%Y-%m-%d %H:%M:%S')
            
            # Check availability with staff_id=None
            is_available = self.appointment_model.check_appointment_availability(
                appt_datetime, 
                staff_id=None,
                duration_minutes=30
            )
            
            if not is_available:
                QMessageBox.warning(self, "Time Slot Unavailable", 
                    "This time slot is already booked. Please choose a different time.")
                return
            
            # Call the model's create_appointment method
            result = self.appointment_model.create_appointment(appointment_data)
            
            if result:
                QMessageBox.information(self, "Success", "Appointment booked successfully!")
                self.accept()
            else:
                # Try a direct database insert as fallback
                try:
                    cursor = self.appointment_model.db.cursor()
                    query = """
                    INSERT INTO appointments (customer_id, staff_id, service_type, appointment_date, notes, status)
                    VALUES (%s, %s, %s, %s, %s, 'Pending')
                    """
                    params = (
                        self.customer_id,
                        None,  # staff_id
                        service_type,
                        appointment_date,
                        notes if notes else ''
                    )
                    
                    cursor.execute(query, params)
                    self.appointment_model.db.commit()
                    rowcount = cursor.rowcount
                    cursor.close()
                    
                    if rowcount > 0:
                        QMessageBox.information(self, "Success", "Appointment booked successfully!")
                        self.accept()
                    else:
                        QMessageBox.warning(self, "Error", 
                            "Failed to book appointment. No rows were inserted.")
                        
                except Exception as db_error:
                    # Error message
                    error_msg = str(db_error)
                    if "foreign key constraint" in error_msg.lower():
                        QMessageBox.warning(self, "Error", 
                            "Invalid customer account. Please contact support.")
                    elif "duplicate entry" in error_msg.lower():
                        QMessageBox.warning(self, "Error", 
                            "This appointment time is already booked.")
                    elif "datetime" in error_msg.lower():
                        QMessageBox.warning(self, "Error", 
                            "Invalid date/time format.")
                    else:
                        QMessageBox.warning(self, "Error", 
                            "Failed to book appointment. Please try again.")
                        
        except ValueError:
            QMessageBox.warning(self, "Error", 
                "Invalid date/time format. Please try again.")
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                "An unexpected error occurred. Please try again.")

class CustomerAppointmentDetailsDialog(QDialog):
    def __init__(self, appointment):
        super().__init__()
        self.appointment = appointment
        self.setStyleSheet("background-color: white; color: black;")
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Appointment Details - #{self.appointment['id']}")
        self.setModal(True)
        self.resize(500, 450)
        
        layout = QVBoxLayout()
        
        # Appointment information group box
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
            }
        """)
        appointment_layout = QFormLayout()
        appointment_layout.addRow("Appointment ID:", QLabel(str(self.appointment['id'])))
        appointment_layout.addRow("Service Type:", QLabel(self.appointment['service_type']))
        
        # Format datetime
        appt_date = self.appointment['appointment_date']
        if isinstance(appt_date, str):
            appt_date = datetime.strptime(appt_date, '%Y-%m-%d %H:%M:%S')
        appointment_layout.addRow("Date & Time:", QLabel(appt_date.strftime('%Y-%m-%d %I:%M %p')))
        
        appointment_group.setLayout(appointment_layout)
        layout.addWidget(appointment_group)
        
        # Staff and status group box
        details_group = QGroupBox("Appointment Details")
        details_group.setStyleSheet("""
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
            }
        """)
        details_layout = QFormLayout()
        
        staff_name = f"{self.appointment.get('staff_first_name', '')} {self.appointment.get('staff_last_name', '')}".strip()
        if not staff_name:
            staff_name = "Not Assigned"
        details_layout.addRow("Assigned Staff:", QLabel(staff_name))
        
        # Status with colored label
        status_label = QLabel(self.appointment['status'])
        if self.appointment['status'] == 'Pending':
            status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        elif self.appointment['status'] == 'Approved':
            status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        elif self.appointment['status'] == 'Completed':
            status_label.setStyleSheet("color: #3498db; font-weight: bold;")
        elif self.appointment['status'] == 'Cancelled':
            status_label.setStyleSheet("color: #9e9e9e; font-weight: bold; font-style: italic;")
        details_layout.addRow("Status:", status_label)
        
        # Notes with colored background
        if self.appointment.get('notes'):
            notes_label = QLabel(self.appointment['notes'])
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet("background-color: #f9d162; color: black; padding: 10px; border-radius: 5px;")
            details_layout.addRow("Notes:", notes_label)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #5ab9ea;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #78d1ff;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
