from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QTimeEdit, QTextEdit,
                             QMessageBox, QHeaderView, QDialog, QFormLayout,
                             QDialogButtonBox)
from PyQt6.QtCore import QDateTime, Qt
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
        self.load_appointments()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("My Appointments")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        
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
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
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
                cancel_btn.clicked.connect(lambda checked, a=appointment: self.cancel_appointment(a['id']))
                actions_layout.addWidget(cancel_btn)
            
            view_btn = QPushButton("Details")
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
        reply = QMessageBox.question(self, "Cancel Appointment", 
                                   "Are you sure you want to cancel this appointment?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.appointment_model.update_appointment_status(appointment_id, 'Cancelled'):
                QMessageBox.information(self, "Success", "Appointment cancelled successfully")
                self.load_appointments()
            else:
                QMessageBox.warning(self, "Error", "Failed to cancel appointment")
    
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
        self.time_edit.setTimeRange(QDateTime.currentDateTime().time(), QDateTime.currentDateTime().time().addSecs(3600*17))
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Any special requirements or notes...")
        
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

class CustomerAppointmentDetailsDialog(QDialog):
    def __init__(self, appointment):
        super().__init__()
        self.appointment = appointment
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Appointment Details - #{self.appointment['id']}")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QFormLayout()
        
        layout.addRow("Appointment ID:", QLabel(str(self.appointment['id'])))
        layout.addRow("Service Type:", QLabel(self.appointment['service_type']))
        
        # Format datetime
        appt_date = self.appointment['appointment_date']
        if isinstance(appt_date, str):
            appt_date = datetime.strptime(appt_date, '%Y-%m-%d %H:%M:%S')
        layout.addRow("Date & Time:", QLabel(appt_date.strftime('%Y-%m-%d %I:%M %p')))
        
        staff_name = f"{self.appointment['staff_first_name']} {self.appointment['staff_last_name']}" if self.appointment['staff_first_name'] else "Not Assigned"
        layout.addRow("Assigned Staff:", QLabel(staff_name))
        layout.addRow("Status:", QLabel(self.appointment['status']))
        
        if self.appointment.get('notes'):
            notes_label = QLabel(self.appointment['notes'])
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet("background: #f8f9fa; padding: 10px; border-radius: 5px;")
            layout.addRow("Notes:", notes_label)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addRow(close_btn)
        
        self.setLayout(layout)