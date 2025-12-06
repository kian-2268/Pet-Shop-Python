from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QDialog, QFormLayout,
                             QDialogButtonBox, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt
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
        self.load_adoption_requests()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("My Adoption Requests")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Adoption requests table
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(6)
        self.requests_table.setHorizontalHeaderLabels([
            "ID", "Pet Name", "Species", "Request Date", "Status", "Actions"
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
        requests = self.adoption_model.get_adoption_requests_by_customer(self.user_id)
        self.requests_table.setRowCount(len(requests))
        
        for row, request in enumerate(requests):
            self.requests_table.setItem(row, 0, QTableWidgetItem(str(request['id'])))
            self.requests_table.setItem(row, 1, QTableWidgetItem(request['pet_name']))
            self.requests_table.setItem(row, 2, QTableWidgetItem(request['species']))
            
            # Format date
            request_date = request['request_date']
            if isinstance(request_date, str):
                from datetime import datetime
                request_date = datetime.strptime(request_date, '%Y-%m-%d %H:%M:%S')
            self.requests_table.setItem(row, 3, QTableWidgetItem(request_date.strftime('%Y-%m-%d')))
            
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
            self.requests_table.setItem(row, 4, status_item)
            
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
            self.requests_table.setCellWidget(row, 5, actions_widget)
    
    def view_request_details(self, request):
        dialog = CustomerAdoptionRequestDetailsDialog(request)
        dialog.exec()
    
    def cancel_request(self, request_id):
        reply = QMessageBox.question(self, "Cancel Request", 
                                   "Are you sure you want to cancel this adoption request?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.adoption_model.update_adoption_status(request_id, 'Cancelled'):
                QMessageBox.information(self, "Success", "Adoption request cancelled")
                self.load_adoption_requests()
            else:
                QMessageBox.warning(self, "Error", "Failed to cancel request")

class CustomerAdoptionRequestDetailsDialog(QDialog):
    def __init__(self, request):
        super().__init__()
        self.request = request
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Adoption Request Details - #{self.request['id']}")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Pet information
        pet_group = QGroupBox("Pet Information")
        pet_layout = QFormLayout()
        pet_layout.addRow("Pet Name:", QLabel(self.request['pet_name']))
        pet_layout.addRow("Species:", QLabel(self.request['species']))
        pet_layout.addRow("Breed:", QLabel(self.request['breed'] or 'Mixed'))
        pet_group.setLayout(pet_layout)
        layout.addWidget(pet_group)
        
        # Request details
        request_group = QGroupBox("Request Details")
        request_layout = QFormLayout()
        request_layout.addRow("Request Date:", QLabel(str(self.request['request_date'])))
        request_layout.addRow("Status:", QLabel(self.request['status']))
        
        if self.request.get('notes'):
            notes_label = QLabel(self.request['notes'])
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet("background: #f8f9fa; padding: 10px; border-radius: 5px;")
            request_layout.addRow("Your Notes:", notes_label)
        
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