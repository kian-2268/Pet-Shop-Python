from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QDialogButtonBox, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt
from models.adoption_model import AdoptionModel
from models.pet_model import PetModel

class AdoptionPanel(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.adoption_model = AdoptionModel(db)
        self.pet_model = PetModel(db)
        self.init_ui()
        self.load_adoption_requests()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Adoption Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Pending", "Approved", "Rejected"])
        self.status_combo.currentTextChanged.connect(self.filter_requests)
        
        filter_layout.addWidget(self.status_combo)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        layout.addSpacing(20)
        
        # Adoption requests table
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(8)
        self.requests_table.setHorizontalHeaderLabels([
            "ID", "Customer", "Pet", "Species", "Request Date", "Status", "Notes", "Actions"
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
    
    def load_adoption_requests(self):
        requests = self.adoption_model.get_adoption_requests()
        self.requests_table.setRowCount(len(requests))
        
        for row, request in enumerate(requests):
            self.requests_table.setItem(row, 0, QTableWidgetItem(str(request['id'])))
            self.requests_table.setItem(row, 1, QTableWidgetItem(f"{request['first_name']} {request['last_name']}"))
            self.requests_table.setItem(row, 2, QTableWidgetItem(request['pet_name']))
            self.requests_table.setItem(row, 3, QTableWidgetItem(request['species']))
            
            # Format date
            request_date = request['request_date']
            if isinstance(request_date, str):
                from datetime import datetime
                request_date = datetime.strptime(request_date, '%Y-%m-%d %H:%M:%S')
            self.requests_table.setItem(row, 4, QTableWidgetItem(request_date.strftime('%Y-%m-%d')))
            
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
            
            self.requests_table.setItem(row, 6, QTableWidgetItem(request.get('notes', '')[:50] + '...' if request.get('notes') and len(request.get('notes')) > 50 else request.get('notes', '')))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            if request['status'] == 'Pending':
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
                approve_btn.clicked.connect(lambda checked, r=request: self.update_request_status(r['id'], 'Approved'))
                actions_layout.addWidget(approve_btn)
                
                reject_btn = QPushButton("Reject")
                reject_btn.setStyleSheet("""
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
                reject_btn.clicked.connect(lambda checked, r=request: self.update_request_status(r['id'], 'Rejected'))
                actions_layout.addWidget(reject_btn)
            
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
            
            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.requests_table.setCellWidget(row, 7, actions_widget)
    
    def filter_requests(self, status):
        if status == "All":
            for row in range(self.requests_table.rowCount()):
                self.requests_table.setRowHidden(row, False)
        else:
            for row in range(self.requests_table.rowCount()):
                status_item = self.requests_table.item(row, 5)
                if status_item and status_item.text() == status:
                    self.requests_table.setRowHidden(row, False)
                else:
                    self.requests_table.setRowHidden(row, True)
    
    def update_request_status(self, request_id, status):
        # For admin, use user_id 1 as approved_by
        if self.adoption_model.update_adoption_status(request_id, status, 1):
            if status == 'Approved':
                # Update pet status to adopted
                query = "UPDATE pets SET status = 'Adopted' WHERE id = (SELECT pet_id FROM adoption_requests WHERE id = %s)"
                self.db.execute_query(query, (request_id,))
            
            QMessageBox.information(self, "Success", f"Adoption request {status.lower()} successfully")
            self.load_adoption_requests()
        else:
            QMessageBox.warning(self, "Error", "Failed to update adoption request")
    
    def view_request_details(self, request):
        dialog = AdoptionRequestDetailsDialog(request, self.pet_model)
        dialog.exec()

class AdoptionRequestDetailsDialog(QDialog):
    def __init__(self, request, pet_model):
        super().__init__()
        self.request = request
        self.pet_model = pet_model
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Adoption Request Details - #{self.request['id']}")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Customer info
        customer_group = QGroupBox("Customer Information")
        customer_layout = QFormLayout()
        customer_layout.addRow("Name:", QLabel(f"{self.request['first_name']} {self.request['last_name']}"))
        customer_layout.addRow("Email:", QLabel(self.request['email']))
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)
        
        # Pet info
        pet_group = QGroupBox("Pet Information")
        pet_layout = QFormLayout()
        pet_layout.addRow("Name:", QLabel(self.request['pet_name']))
        pet_layout.addRow("Species:", QLabel(self.request['species']))
        
        # Get additional pet details
        pet = self.pet_model.get_pet_by_id(self.request['pet_id'])
        if pet:
            pet_layout.addRow("Breed:", QLabel(pet['breed'] or 'Mixed'))
            pet_layout.addRow("Age:", QLabel(str(pet['age'])))
            pet_layout.addRow("Gender:", QLabel(pet['gender']))
        
        pet_group.setLayout(pet_layout)
        layout.addWidget(pet_group)
        
        # Request details
        request_group = QGroupBox("Adoption Request Details")
        request_layout = QFormLayout()
        request_layout.addRow("Request Date:", QLabel(str(self.request['request_date'])))
        request_layout.addRow("Status:", QLabel(self.request['status']))
        
        notes_label = QLabel(self.request.get('notes', 'No notes provided'))
        notes_label.setWordWrap(True)
        notes_label.setStyleSheet("background: #f8f9fa; padding: 10px; border-radius: 5px;")
        request_layout.addRow("Customer Notes:", notes_label)
        
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