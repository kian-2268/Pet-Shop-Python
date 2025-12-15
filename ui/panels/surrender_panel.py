from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QDialogButtonBox, QTextEdit,
                             QLineEdit, QSpinBox, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from models.surrender_model import SurrenderModel

class SurrenderPanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.surrender_model = SurrenderModel(db)
        self.init_ui()
        QTimer.singleShot(0, self.load_surrender_requests) 
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Pet Surrender Requests")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        layout.addWidget(title)
        
        # New request button
        new_request_btn = QPushButton("Surrender a Pet")
        new_request_btn.setStyleSheet("""
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
        new_request_btn.clicked.connect(self.create_surrender_request)
        layout.addWidget(new_request_btn)
        layout.addSpacing(20)
        
        # Requests table
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(7)
        self.requests_table.setHorizontalHeaderLabels([
            "ID", "Pet Name", "Species", "Breed", "Age", "Status", "Actions"
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
        
        self.setLayout(layout)
    
    def load_surrender_requests(self):
        requests = self.surrender_model.get_surrender_requests_by_customer(self.user_id)
        self.requests_table.setRowCount(len(requests))
    
        for row, request in enumerate(requests):
            # Set non-editable for all items
            for col in range(6):  # Columns 0-5 (6 columns total)
                item = QTableWidgetItem()
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.requests_table.setItem(row, col, item)
        
            # Fill in the data
            self.requests_table.item(row, 0).setText(str(request['id']))
            self.requests_table.item(row, 1).setText(request['pet_name'])
            self.requests_table.item(row, 2).setText(request['species'])
            self.requests_table.item(row, 3).setText(request['breed'] or 'Unknown')
            self.requests_table.item(row, 4).setText(str(request['age']))
        
            # Status with color coding
            status = request.get('status', 'Pending')
            self.requests_table.item(row, 5).setText(status)
        
            # Apply different colors for each status
            if status == 'Pending':
                self.requests_table.item(row, 5).setBackground(QColor(255, 255, 0, 100))  # Yellow with transparency
                self.requests_table.item(row, 5).setForeground(Qt.GlobalColor.black)
            elif status == 'Approved':
                self.requests_table.item(row, 5).setBackground(QColor(0, 255, 0, 100))  # Green with transparency
                self.requests_table.item(row, 5).setForeground(Qt.GlobalColor.black)
            elif status == 'Rejected':
                self.requests_table.item(row, 5).setBackground(QColor(255, 0, 0, 100))  # Red with transparency
                self.requests_table.item(row, 5).setForeground(Qt.GlobalColor.white)
            elif status == 'Cancelled':
                self.requests_table.item(row, 5).setBackground(QColor(128, 128, 128, 100))  # Gray with transparency
                self.requests_table.item(row, 5).setForeground(Qt.GlobalColor.white)
                self.requests_table.item(row, 5).setFont(QFont("Arial", 10, QFont.Weight.Bold))
            
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
                        padding: 5px 5px;
                    }
                """)
                actions_layout.addWidget(cancelled_label)
            
            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.requests_table.setCellWidget(row, 6, actions_widget)
    
    def create_surrender_request(self):
        dialog = SurrenderRequestDialog(self.surrender_model, self.user_id)
        dialog.exec()
        self.load_surrender_requests()
    
    def view_request_details(self, request):
        dialog = SurrenderRequestDetailsDialog(request)
        dialog.exec()
    
    def cancel_request(self, request_id):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Cancel Request")
        msg_box.setText("Are you sure you want to cancel this surrender request?")
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
            if self.surrender_model.update_surrender_status(request_id, 'Cancelled'):
                # Success message
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText("Surrender request cancelled")
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
                self.load_surrender_requests()
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
                    QMessageBox QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                error_msg.exec()

class SurrenderRequestDialog(QDialog):
    def __init__(self, surrender_model, customer_id):
        super().__init__()
        self.surrender_model = surrender_model
        self.customer_id = customer_id
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Surrender a Pet")
        self.setModal(True)
        self.resize(500, 400)
        self.setStyleSheet("background-color: white; color: black;")
        
        layout = QFormLayout()
        layout.setSpacing(15)
        
        self.pet_name_input = QLineEdit()
        self.species_combo = QComboBox()
        self.species_combo.addItems(["Dog", "Cat", "Bird", "Rabbit", "Other"])
        
        self.breed_input = QLineEdit()
        self.age_input = QSpinBox()
        self.age_input.setRange(0, 30)
        
        self.reason_input = QTextEdit()
        self.reason_input.setMaximumHeight(100)
        self.reason_input.setPlaceholderText("Please explain why you need to surrender this pet...")
        
        # Style inputs
        for widget in [self.pet_name_input, self.breed_input]:
            widget.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    color: black;
                }
            """)
        
        self.reason_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                color: black;
                background-color: #f9d162
            }
        """)
        
        layout.addRow("Pet Name *:", self.pet_name_input)
        layout.addRow("Species *:", self.species_combo)
        layout.addRow("Breed:", self.breed_input)
        layout.addRow("Age (years):", self.age_input)
        layout.addRow("Reason for Surrender *:", self.reason_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.submit_request)
        button_box.rejected.connect(self.reject)
        
        layout.addRow(button_box)
        self.setLayout(layout)
    
    def submit_request(self):
        pet_name = self.pet_name_input.text().strip()
        species = self.species_combo.currentText()
        breed = self.breed_input.text().strip()
        age = self.age_input.value()
        reason = self.reason_input.toPlainText().strip()
        
        if not pet_name or not reason:
            QMessageBox.warning(self, "Error", "Please fill in all required fields")
            return
        
        request_data = {
            'customer_id': self.customer_id,
            'pet_name': pet_name,
            'species': species,
            'breed': breed,
            'age': age,
            'reason': reason
        }
        
        if self.surrender_model.create_surrender_request(request_data):
            QMessageBox.information(self, "Success", "Surrender request submitted for review")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to submit surrender request")

class SurrenderRequestDetailsDialog(QDialog):
    def __init__(self, request):
        super().__init__()
        self.request = request
        self.setStyleSheet("background-color: white; color: black;")
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Surrender Request Details - #{self.request['id']}")
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
        pet_layout.addRow("Breed:", QLabel(self.request['breed'] or 'Unknown'))
        pet_layout.addRow("Age:", QLabel(str(self.request['age'])))
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
        status_label = QLabel(self.request.get('status', 'Pending'))
        if self.request.get('status', 'Pending') == 'Pending':
            status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        elif self.request.get('status', 'Pending') == 'Approved':
            status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        elif self.request.get('status', 'Pending') == 'Rejected':
            status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        elif self.request.get('status', 'Pending') == 'Cancelled':
            status_label.setStyleSheet("color: #9e9e9e; font-weight: bold; font-style: italic;")
        request_layout.addRow("Status:", status_label)
        
        # Reason field with colored background 
        if self.request.get('reason'):
            reason_label = QLabel(self.request['reason'])
            reason_label.setWordWrap(True)
            reason_label.setStyleSheet("background-color: #f9d162; color: black; padding: 5px; border-radius: 5px;")
            request_layout.addRow("Reason for Surrender:", reason_label)
        
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
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #78d1ff;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
