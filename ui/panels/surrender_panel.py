from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QDialogButtonBox, QTextEdit,
                             QLineEdit, QSpinBox, QGroupBox)
from PyQt6.QtCore import Qt
from models.surrender_model import SurrenderModel

class SurrenderPanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.surrender_model = SurrenderModel(db)
        self.init_ui()
        self.load_surrender_requests()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Pet Surrender Requests")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
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
        
        self.requests_table.setStyleSheet("""
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
        
        self.requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.requests_table)
        
        self.setLayout(layout)
    
    def load_surrender_requests(self):
        requests = self.surrender_model.get_surrender_requests_by_customer(self.user_id)
        self.requests_table.setRowCount(len(requests))
        
        for row, request in enumerate(requests):
            self.requests_table.setItem(row, 0, QTableWidgetItem(str(request['id'])))
            self.requests_table.setItem(row, 1, QTableWidgetItem(request['pet_name']))
            self.requests_table.setItem(row, 2, QTableWidgetItem(request['species']))
            self.requests_table.setItem(row, 3, QTableWidgetItem(request['breed'] or 'Unknown'))
            self.requests_table.setItem(row, 4, QTableWidgetItem(str(request['age'])))
            
            # Status with color coding
            status_item = QTableWidgetItem(request['status'])
            if request['status'] == 'Pending':
                status_item.setBackground(Qt.GlobalColor.yellow)
            elif request['status'] == 'Approved':
                status_item.setBackground(Qt.GlobalColor.green)
                status_item.setForeground(Qt.GlobalColor.white)
            elif request['status'] == 'Rejected':
                status_item.setBackground(Qt.GlobalColor.red)
                status_item.setForeground(Qt.GlobalColor.white)
            self.requests_table.setItem(row, 5, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            view_btn = QPushButton("View Details")
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
            
            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.requests_table.setCellWidget(row, 6, actions_widget)
    
    def create_surrender_request(self):
        dialog = SurrenderRequestDialog(self.surrender_model, self.user_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Success", "Surrender request submitted successfully!")
            self.load_surrender_requests()
    
    def view_request_details(self, request):
        dialog = SurrenderRequestDetailsDialog(request)
        dialog.exec()
    
    def cancel_request(self, request_id):
        reply = QMessageBox.question(self, "Cancel Request", 
                                   "Are you sure you want to cancel this surrender request?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.surrender_model.update_surrender_status(request_id, 'Cancelled'):
                QMessageBox.information(self, "Success", "Surrender request cancelled")
                self.load_surrender_requests()
            else:
                QMessageBox.warning(self, "Error", "Failed to cancel request")

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
                }
            """)
        
        self.reason_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
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
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Surrender Request Details - #{self.request['id']}")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Pet information
        pet_group = QGroupBox("Pet Information")
        pet_layout = QFormLayout()
        pet_layout.addRow("Pet Name:", QLabel(self.request['pet_name']))
        pet_layout.addRow("Species:", QLabel(self.request['species']))
        pet_layout.addRow("Breed:", QLabel(self.request['breed'] or 'Unknown'))
        pet_layout.addRow("Age:", QLabel(str(self.request['age'])))
        pet_group.setLayout(pet_layout)
        layout.addWidget(pet_group)
        
        # Request details
        request_group = QGroupBox("Request Details")
        request_layout = QFormLayout()
        request_layout.addRow("Request Date:", QLabel(str(self.request['request_date'])))
        request_layout.addRow("Status:", QLabel(self.request['status']))
        
        reason_label = QLabel(self.request['reason'])
        reason_label.setWordWrap(True)
        reason_label.setStyleSheet("background: #f8f9fa; padding: 10px; border-radius: 5px;")
        request_layout.addRow("Reason:", reason_label)
        
        request_group.setLayout(request_layout)
        layout.addWidget(request_group)
        
        # Close button
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
        layout.addWidget(close_btn)
        
        self.setLayout(layout)