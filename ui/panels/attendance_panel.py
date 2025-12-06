from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDateEdit, QMessageBox, QHeaderView, QGroupBox)
from PyQt6.QtCore import QDateTime, Qt
from datetime import datetime
from models.attendance_model import AttendanceModel

class AttendancePanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.attendance_model = AttendanceModel(db)
        self.init_ui()
        self.load_attendance()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Attendance Tracking")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Check-in/out buttons
        self.checkin_btn = QPushButton("Check In")
        self.checkin_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #219a52;
            }
        """)
        self.checkin_btn.clicked.connect(self.check_in)
        
        self.checkout_btn = QPushButton("Check Out")
        self.checkout_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        self.checkout_btn.clicked.connect(self.check_out)
        
        header_layout.addWidget(self.checkin_btn)
        header_layout.addWidget(self.checkout_btn)
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        
        # Today's status
        today_group = QGroupBox("Today's Status")
        today_layout = QHBoxLayout()
        
        self.status_label = QLabel("Not checked in today")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        
        today_layout.addWidget(self.status_label)
        today_layout.addStretch()
        today_group.setLayout(today_layout)
        layout.addWidget(today_group)
        layout.addSpacing(20)
        
        # Attendance history
        history_group = QGroupBox("Attendance History")
        history_layout = QVBoxLayout()
        
        # Date filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Month:"))
        self.month_combo = QDateEdit()
        self.month_combo.setDate(QDateTime.currentDateTime().date())
        self.month_combo.setDisplayFormat("MMMM yyyy")
        self.month_combo.setCalendarPopup(True)
        self.month_combo.dateChanged.connect(self.load_attendance)
        filter_layout.addWidget(self.month_combo)
        filter_layout.addStretch()
        history_layout.addLayout(filter_layout)
        
        # Attendance table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(5)
        self.attendance_table.setHorizontalHeaderLabels([
            "Date", "Check In", "Check Out", "Hours Worked", "Status"
        ])
        
        self.attendance_table.setStyleSheet("""
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
        
        self.attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        history_layout.addWidget(self.attendance_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        self.setLayout(layout)
        self.update_today_status()
    
    def update_today_status(self):
        today = datetime.now().date()
        today_attendance = self.attendance_model.get_attendance_by_date(self.user_id, today)
        
        if today_attendance:
            if today_attendance['check_out']:
                self.status_label.setText("Checked out for today")
                self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
                self.checkin_btn.setEnabled(False)
                self.checkout_btn.setEnabled(False)
            else:
                self.status_label.setText("Checked in - Working")
                self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
                self.checkin_btn.setEnabled(False)
                self.checkout_btn.setEnabled(True)
        else:
            self.status_label.setText("Not checked in today")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
            self.checkin_btn.setEnabled(True)
            self.checkout_btn.setEnabled(False)
    
    def check_in(self):
        if self.attendance_model.check_in(self.user_id):
            QMessageBox.information(self, "Success", "Checked in successfully!")
            self.update_today_status()
            self.load_attendance()
        else:
            QMessageBox.warning(self, "Error", "Failed to check in")
    
    def check_out(self, user_id):
        try:
            today = datetime.now().date()
            current_time = datetime.now()
        
            print(f"=== CHECK-OUT DEBUG ===")
            print(f"User ID: {user_id}")
            print(f"Today: {today}")
            print(f"Current Time: {current_time}")
        
            # Get today's attendance record
            query = "SELECT id, check_in FROM attendance WHERE staff_id = %s AND date = %s AND check_out IS NULL"
            result = self.db.execute_query(query, (user_id, today))
        
            print(f"Query result: {result}")
        
            if not result or len(result) == 0:
                print("No check-in found for today")
                return False
        
            # Extract data from dictionary
            record = result[0]
            record_id = record['id']
            check_in_time = record['check_in']
        
            print(f"Record ID: {record_id}")
            print(f"Check-in Time: {check_in_time}")
            print(f"Check-in Time Type: {type(check_in_time)}")
        
            if not check_in_time:
                print("No check-in time found")
                return False
        
            # Calculate hours worked
            hours_worked = (current_time - check_in_time).total_seconds() / 3600.0
            print(f"Hours worked: {hours_worked:.2f}")
        
            # Update the record
            update_query = """
                UPDATE attendance 
                SET check_out = %s, hours_worked = %s 
                WHERE id = %s
            """
            print(f"Update query: {update_query}")
            print(f"Update params: ({current_time}, {hours_worked}, {record_id})")
        
            success = self.db.execute_query(update_query, (current_time, hours_worked, record_id))
            print(f"Update success: {success}")
        
            # Check if update actually worked by querying the record again
            if success:
                verify_query = "SELECT check_out, hours_worked FROM attendance WHERE id = %s"
                verify_result = self.db.execute_query(verify_query, (record_id,))
                print(f"Verification result: {verify_result}")
        
            return bool(success)
        
        except Exception as e:
            print(f"Error during check-out: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_attendance(self):
        selected_date = self.month_combo.date().toPyDate()
        month_start = selected_date.replace(day=1)
        
        attendance = self.attendance_model.get_attendance_by_month(self.user_id, month_start)
        self.attendance_table.setRowCount(len(attendance))
        
        for row, record in enumerate(attendance):
            # Date
            self.attendance_table.setItem(row, 0, QTableWidgetItem(record['date'].strftime('%Y-%m-%d')))
            
            # Check-in - Handle datetime objects
            check_in = record['check_in']
            if check_in:
                if isinstance(check_in, datetime):
                    check_in_str = check_in.strftime('%H:%M')
                elif hasattr(check_in, 'strftime'):  # It's a datetime-like object
                    check_in_str = check_in.strftime('%H:%M')
                else:
                    check_in_str = str(check_in)
            else:
                check_in_str = 'N/A'
            self.attendance_table.setItem(row, 1, QTableWidgetItem(check_in_str))
            
            # Check-out - Handle datetime objects
            check_out = record['check_out']
            if check_out:
                if isinstance(check_out, datetime):
                    check_out_str = check_out.strftime('%H:%M')
                elif hasattr(check_out, 'strftime'):  # It's a datetime-like object
                    check_out_str = check_out.strftime('%H:%M')
                else:
                    check_out_str = str(check_out)
            else:
                check_out_str = 'N/A'
            self.attendance_table.setItem(row, 2, QTableWidgetItem(check_out_str))
            
            # Hours worked
            hours_worked = record['hours_worked'] or 0
            self.attendance_table.setItem(row, 3, QTableWidgetItem(f"{hours_worked:.2f}"))
            
            # Status
            status_item = QTableWidgetItem()
            if record['check_in'] and record['check_out']:
                status_item.setText("Completed")
                status_item.setBackground(Qt.GlobalColor.green)
                status_item.setForeground(Qt.GlobalColor.white)
            elif record['check_in'] and not record['check_out']:
                status_item.setText("In Progress")
                status_item.setBackground(Qt.GlobalColor.yellow)
            else:
                status_item.setText("Absent")
                status_item.setBackground(Qt.GlobalColor.red)
                status_item.setForeground(Qt.GlobalColor.white)
            
            self.attendance_table.setItem(row, 4, status_item)