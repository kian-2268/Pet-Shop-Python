from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QDialog, QFormLayout,
                             QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from models.adoption_model import AdoptionModel
from models.pet_model import PetModel

class AdoptionRequestPanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.adoption_model = AdoptionModel(db)
        self.pet_model = PetModel(db)
        self.init_ui()
        QTimer.singleShot(0, self.load_adoption_requests) 
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("My Adoption Requests")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        layout.addWidget(title)
        
        # Adoption requests table
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(6)
        self.requests_table.setHorizontalHeaderLabels([
            "ID", "Pet Name", "Species", "Request Date", "Status", "Actions"
        ])

        # Make table uneditable
        self.requests_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.requests_table.setStyleSheet("""
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
        
        self.requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.requests_table)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #5ab9ea;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #78d1ff;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_adoption_requests)
        layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(layout)
    
    def load_adoption_requests(self):
        requests = self.adoption_model.get_adoption_requests_by_customer(self.user_id)
        self.requests_table.setRowCount(len(requests))
        
        for row, request in enumerate(requests):
            # Set non-editable for all items
            for col in range(5):  # Columns 0-4
                item = QTableWidgetItem()
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.requests_table.setItem(row, col, item)
            
            self.requests_table.item(row, 0).setText(str(request['id']))
            self.requests_table.item(row, 1).setText(request['pet_name'])
            self.requests_table.item(row, 2).setText(request['species'])
            
            # Format date
            request_date = request['request_date']
            if isinstance(request_date, str):
                from datetime import datetime
                request_date = datetime.strptime(request_date, '%Y-%m-%d %H:%M:%S')
            self.requests_table.item(row, 3).setText(request_date.strftime('%Y-%m-%d'))
            
            # Status with color coding
            status = request['status']
            self.requests_table.item(row, 4).setText(status)
            
            # Apply different colors for each status
            if status == 'Pending':
                self.requests_table.item(row, 4).setBackground(QColor(255, 255, 0, 100))  # Yellow with transparency
                self.requests_table.item(row, 4).setForeground(Qt.GlobalColor.black)
            elif status == 'Approved':
                self.requests_table.item(row, 4).setBackground(QColor(0, 255, 0, 100))  # Green with transparency
                self.requests_table.item(row, 4).setForeground(Qt.GlobalColor.black)
            elif status == 'Rejected':
                self.requests_table.item(row, 4).setBackground(QColor(255, 0, 0, 100))  # Red with transparency
                self.requests_table.item(row, 4).setForeground(Qt.GlobalColor.white)
            elif status == 'Cancelled':
                self.requests_table.item(row, 4).setBackground(QColor(128, 128, 128, 100))  # Gray with transparency
                self.requests_table.item(row, 4).setForeground(Qt.GlobalColor.white)
                self.requests_table.item(row, 4).setFont(QFont("Arial", 10, QFont.Weight.Bold))
            
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
            view_btn.clicked.connect(lambda checked, r=request: self.view_request_details(r))
            actions_layout.addWidget(view_btn)
            
            # Show cancel button only for Pending status
            if request['status'] == 'Pending':
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
                cancel_btn.clicked.connect(lambda checked, r=request: self.cancel_request(r['id']))
                actions_layout.addWidget(cancel_btn)
            # For cancelled status, show a disabled button or message
            elif request['status'] == 'Cancelled':
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
            self.requests_table.setCellWidget(row, 5, actions_widget)
    
    def refresh_adoption_requests(self):
        """Public method to refresh adoption requests from anywhere"""
        QTimer.singleShot(0, self.load_adoption_requests)
    
    def view_request_details(self, request):
        dialog = CustomerAdoptionRequestDetailsDialog(request)
        dialog.exec()
    
    def cancel_request(self, request_id):
        # Question dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Cancel Request")
        msg_box.setText("Are you sure you want to cancel this adoption request?")
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
            if self.adoption_model.update_adoption_status(request_id, 'Cancelled'):
                # Success message
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText("Adoption request cancelled")
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
                self.refresh_adoption_requests() 
            else:
                # Error message
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Error")
                error_msg.setText("Failed to cancel request")
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
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                error_msg.exec()

class CustomerAdoptionRequestDetailsDialog(QDialog):
    def __init__(self, request):
        super().__init__()
        self.request = request
        self.setStyleSheet("background-color: white; color: black;")
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Adoption Request Details - #{self.request['id']}")
        self.setModal(True)
        self.resize(500, 450)
        
        layout = QVBoxLayout()
        
        # Pet information
        pet_group = QGroupBox("Pet Information")
        pet_group.setStyleSheet("""
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
        pet_layout = QFormLayout()
        pet_layout.addRow("Pet Name:", QLabel(self.request['pet_name']))
        pet_layout.addRow("Species:", QLabel(self.request['species']))
        pet_layout.addRow("Breed:", QLabel(self.request['breed'] or 'Mixed'))
        pet_group.setLayout(pet_layout)
        layout.addWidget(pet_group)
        
        # Request details with status color
        request_group = QGroupBox("Request Details")
        request_group.setStyleSheet("""
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
        request_layout = QFormLayout()
        request_layout.addRow("Request Date:", QLabel(str(self.request['request_date'])))
        
        # Status with colored label
        status_label = QLabel(self.request['status'])
        if self.request['status'] == 'Pending':
            status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        elif self.request['status'] == 'Approved':
            status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        elif self.request['status'] == 'Rejected':
            status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        elif self.request['status'] == 'Cancelled':
            status_label.setStyleSheet("color: #9e9e9e; font-weight: bold; font-style: italic;")
        request_layout.addRow("Status:", status_label)
        
        if self.request.get('notes'):
            notes_label = QLabel(self.request['notes'])
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet("background-color: #f9d162; color: black; padding: 5px; border-radius: 5px;")
            request_layout.addRow("Your Notes:", notes_label)
        
        request_group.setLayout(request_layout)
        layout.addWidget(request_group)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #5ab9ea;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #78d1ff;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
