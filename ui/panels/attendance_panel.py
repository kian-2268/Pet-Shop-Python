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
        self.setStyleSheet("background-color: white; color: black;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        title = QLabel("Attendance Tracking")
        title.setStyleSheet("""
            background-color: white;
            font-size: 25px; 
            font-weight: bold; 
            color: black;
            padding: 10px 0;
        """)
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
                min-width: 100px;
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
                min-width: 100px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        self.checkout_btn.clicked.connect(self.check_out)
        
        header_layout.addWidget(self.checkin_btn)
        header_layout.addWidget(self.checkout_btn)
        
        layout.addWidget(header_widget)
        layout.addSpacing(10)
        
        # Today's status
        today_group = QGroupBox("Today's Status")
        today_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: black;
            }
        """)
        
        today_widget = QWidget()
        today_layout = QHBoxLayout(today_widget)
        
        self.status_label = QLabel("Not checked in today")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        
        today_layout.addWidget(self.status_label)
        today_layout.addStretch()
        today_group.setLayout(today_layout)
        layout.addWidget(today_group)
        layout.addSpacing(10)
        
        # Attendance history
        history_group = QGroupBox("Attendance History")
        history_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: black;
            }
        """)
        
        history_layout = QVBoxLayout()
        
        # Date filter
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_label = QLabel("Month:")
        filter_label.setStyleSheet("""
            QLabel {    
                background-color: white;
                color: black;
                padding: 5px 10px;
            }
        """)
        filter_layout.addWidget(filter_label)
        
        self.month_combo = QDateEdit()
        self.month_combo.setDate(QDateTime.currentDateTime().date())
        self.month_combo.setDisplayFormat("MMMM yyyy")
        self.month_combo.setCalendarPopup(True)
        self.month_combo.setStyleSheet("""
            QDateEdit {
                color: black;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #ddd;
                border-left-style: solid;
            }
        """)
        self.month_combo.dateChanged.connect(self.load_attendance)
        filter_layout.addWidget(self.month_combo)
        filter_layout.addStretch()
        history_layout.addWidget(filter_widget)
        
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
            msg = QMessageBox(self)
            msg.setWindowTitle("Success")
            msg.setText("Checked in successfully!")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStyleSheet("""
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
            msg.exec()
            self.update_today_status()
            self.load_attendance()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("Failed to check in")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet("""
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
            msg.exec()
    
    def check_out(self):
        if self.attendance_model.check_out(self.user_id):
            msg = QMessageBox(self)
            msg.setWindowTitle("Success")
            msg.setText("Checked out successfully!")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStyleSheet("""
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
            msg.exec()
            self.update_today_status()
            self.load_attendance()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("Failed to check out")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet("""
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
            msg.exec()
    
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
                status_item.setForeground(Qt.GlobalColor.white)
                status_item.setBackground(Qt.GlobalColor.darkGreen)
            elif record['check_in'] and not record['check_out']:
                status_item.setText("In Progress")
                status_item.setForeground(Qt.GlobalColor.black)
                status_item.setBackground(Qt.GlobalColor.yellow)
            else:
                status_item.setText("Absent")
                status_item.setForeground(Qt.GlobalColor.white)
                status_item.setBackground(Qt.GlobalColor.darkRed)
            
            self.attendance_table.setItem(row, 4, status_item)
