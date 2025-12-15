from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QTextEdit,
                             QComboBox, QDateEdit, QGroupBox, QScrollArea, 
                             QGridLayout)
from PyQt6.QtCore import Qt, QDateTime
from datetime import datetime
from models.surrender_model import SurrenderModel
from models.pet_model import PetModel

class SurrenderManagementPanel(QWidget):
    def __init__(self, db, user_type='admin'):
        super().__init__()
        self.db = db
        self.user_type = user_type
        self.surrender_model = SurrenderModel(db)
        self.pet_model = PetModel(db)
        self.init_ui()
        self.load_surrender_requests()
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;") 
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header 
        header_layout = QHBoxLayout()
        title = QLabel("Surrender Management")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Filters 
        filter_layout = QHBoxLayout()
        
        # Filter labels with white background
        status_label = QLabel("Status:")
        status_label.setStyleSheet("""
            QLabel {    
                background-color: #f9fafb;
                color: black;
                padding: 5px 10px;
            }
        """)
        filter_layout.addWidget(status_label)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Pending", "Approved", "Rejected", "Cancelled"])
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
        self.status_combo.currentTextChanged.connect(self.filter_requests)
        filter_layout.addWidget(self.status_combo)
        
        # Date filter labels 
        date_from_label = QLabel("Date From:")
        date_from_label.setStyleSheet("""
            QLabel {    
                background-color: #f9fafb;
                color: black;
                padding: 5px 10px;
                margin-left: 10px;
            }
        """)
        filter_layout.addWidget(date_from_label)
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDateTime.currentDateTime().date().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("""
            QDateEdit {
                color: black;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        filter_layout.addWidget(self.start_date)
        
        date_to_label = QLabel("To:")
        date_to_label.setStyleSheet("""
            QLabel {    
                background-color: #f9fafb;
                color: black;
                padding: 5px 10px;
            }
        """)
        filter_layout.addWidget(date_to_label)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDateTime.currentDateTime().date())
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("""
            QDateEdit {
                color: black;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        filter_layout.addWidget(self.end_date)
        
        apply_btn = QPushButton("Apply Filter")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        apply_btn.clicked.connect(self.apply_date_filter)
        filter_layout.addWidget(apply_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        layout.addSpacing(20)
        
        # Quick stats 
        stats_layout = QHBoxLayout()
        
        self.total_requests_label = QLabel("Total Requests: 0")
        self.total_requests_label.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                color: #3498db;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        
        self.pending_requests_label = QLabel("Pending Requests: 0")
        self.pending_requests_label.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                color: #f39c12;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        
        self.approved_requests_label = QLabel("Approved Requests: 0")
        self.approved_requests_label.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                color: #27ae60;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        
        stats_layout.addWidget(self.total_requests_label)
        stats_layout.addWidget(self.pending_requests_label)
        stats_layout.addWidget(self.approved_requests_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        layout.addSpacing(20)
        
        # Surrender requests table 
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(9)
        self.requests_table.setHorizontalHeaderLabels([
            "ID", "Customer", "Pet Name", "Species", "Breed", "Age", 
            "Request Date", "Status", "Actions"
        ])
        
        # Style the table 
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
        
        # Set column resize modes 
        header = self.requests_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Customer
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Pet Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Species
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Breed
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Age
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Request Date
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Actions
        
        layout.addWidget(self.requests_table)
        
        self.setLayout(layout)
    
    def load_surrender_requests(self):
        try:
            # Get filter status
            status_filter = self.status_combo.currentText()
            status = None if status_filter == "All" else status_filter
            
            # Get all surrender requests using the model
            requests = self.surrender_model.get_all_surrender_requests(status)
            
            if requests is False:
                QMessageBox.warning(self, "Error", "Failed to load surrender requests.")
                return
            
            self.display_requests(requests)
            self.update_stats(requests)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load surrender requests: {str(e)}")
    
    def display_requests(self, requests):
        self.requests_table.setRowCount(len(requests))
        
        for row_idx, request in enumerate(requests):
            self.requests_table.setItem(row_idx, 0, QTableWidgetItem(str(request['id'])))
            
            # Customer
            customer_name = f"{request['first_name']} {request['last_name']}"
            self.requests_table.setItem(row_idx, 1, QTableWidgetItem(customer_name))
            
            # Pet Name
            self.requests_table.setItem(row_idx, 2, QTableWidgetItem(request['pet_name']))
            
            # Species
            self.requests_table.setItem(row_idx, 3, QTableWidgetItem(request['species']))
            
            # Breed
            self.requests_table.setItem(row_idx, 4, QTableWidgetItem(request['breed']))
            
            # Age
            age_text = f"{request['age']} years" if request['age'] else "Unknown"
            self.requests_table.setItem(row_idx, 5, QTableWidgetItem(age_text))
            
            # Request Date
            request_date = request['request_date']
            if isinstance(request_date, str):
                request_date = datetime.strptime(request_date, '%Y-%m-%d %H:%M:%S')
            self.requests_table.setItem(row_idx, 6, QTableWidgetItem(request_date.strftime('%Y-%m-%d %H:%M')))
            
            # Status with foreground color only (no background)
            status_item = QTableWidgetItem(request['status'])
            if request['status'] == 'Pending':
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            elif request['status'] == 'Approved':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif request['status'] == 'Rejected':
                status_item.setForeground(Qt.GlobalColor.darkRed)
            elif request['status'] == 'Cancelled':
                status_item.setForeground(Qt.GlobalColor.darkGray)
            self.requests_table.setItem(row_idx, 7, status_item)
            
            # Actions buttons 
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background-color: white;")
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            # View details button for all requests
            view_btn = QPushButton("View")
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
            view_btn.clicked.connect(lambda checked, req=request: self.view_request_details(req))
            actions_layout.addWidget(view_btn)
            
            # Only show action buttons for pending requests
            if request['status'] == 'Pending':
                # Approve button
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
                approve_btn.clicked.connect(lambda checked, req=request: self.process_request(req, 'Approved'))
                actions_layout.addWidget(approve_btn)
                
                # Reject button
                reject_btn = QPushButton("Reject")
                reject_btn.setMinimumHeight(20)
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
                reject_btn.clicked.connect(lambda checked, req=request: self.process_request(req, 'Rejected'))
                actions_layout.addWidget(reject_btn)
            
            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.requests_table.setCellWidget(row_idx, 8, actions_widget)
    
    def update_stats(self, requests):
        total_requests = len(requests)
        pending_requests = sum(1 for request in requests if request['status'] == 'Pending')
        approved_requests = sum(1 for request in requests if request['status'] == 'Approved')
        
        self.total_requests_label.setText(f"Total Requests: {total_requests}")
        self.pending_requests_label.setText(f"Pending Requests: {pending_requests}")
        self.approved_requests_label.setText(f"Approved Requests: {approved_requests}")
    
    def filter_requests(self, status):
        if status == "All":
            for row in range(self.requests_table.rowCount()):
                self.requests_table.setRowHidden(row, False)
        else:
            for row in range(self.requests_table.rowCount()):
                status_item = self.requests_table.item(row, 7)
                if status_item and status_item.text() == status:
                    self.requests_table.setRowHidden(row, False)
                else:
                    self.requests_table.setRowHidden(row, True)
    
    def apply_date_filter(self):
        start_date = self.start_date.date().toString('yyyy-MM-dd')
        end_date = self.end_date.date().toString('yyyy-MM-dd')
        
        all_requests = self.surrender_model.get_all_surrender_requests()
        filtered_requests = []
        
        for request in all_requests:
            request_date = request['request_date']
            if isinstance(request_date, str):
                request_date = datetime.strptime(request_date, '%Y-%m-%d %H:%M:%S')
            
            if start_date <= request_date.strftime('%Y-%m-%d') <= end_date:
                filtered_requests.append(request)
        
        self.display_requests(filtered_requests)
        self.update_stats(filtered_requests)
    
    def process_request(self, request, action):
        # Confirmation dialog 
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"Confirm {action}")
        msg_box.setText(f"Are you sure you want to {action.lower()} this surrender request?")
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
            try:
                # Update surrender status
                success = self.surrender_model.update_surrender_status(
                    request['id'], 
                    action, 
                    self.user_type
                )
                
                if success:
                    # If approved, add pet to pets table
                    if action == 'Approved':
                        # Prepare pet data with all required fields for PetModel.add_pet()
                        pet_data = {
                            'name': request['pet_name'],
                            'species': request['species'],
                            'breed': request['breed'],
                            'age': request.get('age', 0) or 0,  # Default to 0 if None
                            'gender': 'Unknown',  # Required field
                            'price': 0.00,  # Default price for surrendered pets
                            'description': f"Surrendered pet. Reason: {request.get('reason', 'No reason provided')}",
                            'status': 'Available',
                            'health_status': 'Unknown',  # Required field
                            'vaccination_status': 'Unknown',  # Required field
                            'image_path': None  # No image initially
                        }
                        
                        # Add pet to database using PetModel
                        # created_by parameter is required by PetModel.add_pet()
                        pet_result = self.pet_model.add_pet(pet_data, created_by=self.user_type)
                        
                        if not pet_result:
                            QMessageBox.warning(self, "Warning", 
                                              f"Request {action.lower()} but failed to add pet to database.")
                        
                        # Optional: Update surrender request with the new pet ID
                        try:
                            # Get the last inserted pet ID
                            pet_id_query = "SELECT LAST_INSERT_ID() as pet_id"
                            pet_id_result = self.db.execute_query(pet_id_query)
                            if pet_id_result and pet_id_result[0]['pet_id']:
                                new_pet_id = pet_id_result[0]['pet_id']
                                # Update surrender request with pet_id
                                update_query = "UPDATE surrender_requests SET pet_id = %s WHERE id = %s"
                                self.db.execute_query(update_query, (new_pet_id, request['id']))
                        except Exception as e:
                            print(f"Note: Could not link pet to surrender request: {e}")
                    
                    # Success message 
                    success_msg = QMessageBox(self)
                    success_msg.setWindowTitle("Success")
                    success_msg.setText(f"Surrender request {action.lower()} successfully")
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
                    error_msg.setText("Failed to update surrender request")
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
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to process request: {str(e)}")
    
    def view_request_details(self, request):
        dialog = SurrenderRequestDetailsDialog(request)
        dialog.exec()

class SurrenderRequestDetailsDialog(QDialog):
    def __init__(self, request):
        super().__init__()
        self.request = request
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Surrender Request Details - #{self.request['id']}")
        self.setModal(True)
        self.setStyleSheet("background-color: white; color: black;")
        self.resize(700, 500)  
        
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
        
        # Customer Information Group 
        customer_group = QGroupBox("Customer Information")
        customer_group.setStyleSheet("""
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
        customer_layout = QGridLayout()
        customer_layout.setHorizontalSpacing(20)
        customer_layout.setVerticalSpacing(10)
        
        customer_layout.addWidget(QLabel("Name:"), 0, 0)
        customer_name = f"{self.request['first_name']} {self.request['last_name']}"
        customer_layout.addWidget(QLabel(customer_name), 0, 1)
        
        customer_layout.addWidget(QLabel("Email:"), 0, 2)
        customer_layout.addWidget(QLabel(self.request['email']), 0, 3)
        
        customer_group.setLayout(customer_layout)
        container_layout.addWidget(customer_group)
        
        # Pet Information Group 
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
                color: black;
            }
        """)
        pet_layout = QGridLayout()
        pet_layout.setHorizontalSpacing(20)
        pet_layout.setVerticalSpacing(10)
        
        pet_layout.addWidget(QLabel("Pet Name:"), 0, 0)
        pet_layout.addWidget(QLabel(self.request['pet_name']), 0, 1)
        
        pet_layout.addWidget(QLabel("Species:"), 0, 2)
        pet_layout.addWidget(QLabel(self.request['species']), 0, 3)
        
        pet_layout.addWidget(QLabel("Breed:"), 1, 0)
        pet_layout.addWidget(QLabel(self.request['breed']), 1, 1)
        
        pet_layout.addWidget(QLabel("Age:"), 1, 2)
        age_text = f"{self.request['age']} years" if self.request['age'] else "Unknown"
        pet_layout.addWidget(QLabel(age_text), 1, 3)
        
        pet_group.setLayout(pet_layout)
        container_layout.addWidget(pet_group)
        
        # Surrender Request Details Group 
        request_group = QGroupBox("Surrender Request Details")
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
                color: black;
            }
        """)
        request_layout = QGridLayout()
        request_layout.setHorizontalSpacing(20)
        request_layout.setVerticalSpacing(10)
        
        request_layout.addWidget(QLabel("Request Date:"), 0, 0)
        request_date = self.request['request_date']
        if isinstance(request_date, str):
            request_date = datetime.strptime(request_date, '%Y-%m-%d %H:%M:%S')
        request_layout.addWidget(QLabel(request_date.strftime('%Y-%m-%d %H:%M')), 0, 1)
        
        request_layout.addWidget(QLabel("Status:"), 0, 2)
        status_label = QLabel(self.request['status'])
        if self.request['status'] == 'Pending':
            status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        elif self.request['status'] == 'Approved':
            status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        elif self.request['status'] == 'Rejected':
            status_label.setStyleSheet("color: #9e9e9e; font-weight: bold; font-style: italic;")
        elif self.request['status'] == 'Cancelled':
            status_label.setStyleSheet("color: #9e9e9e; font-weight: bold; font-style: italic;")
        request_layout.addWidget(status_label, 0, 3)
        
        request_layout.addWidget(QLabel("Reason for Surrender:"), 1, 0)
        reason_text = QTextEdit()
        reason_text.setPlainText(self.request.get('reason', 'No reason provided'))
        reason_text.setReadOnly(True)
        reason_text.setMaximumHeight(100)
        reason_text.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        request_layout.addWidget(reason_text, 1, 1, 1, 3)
        
        request_group.setLayout(request_layout)
        container_layout.addWidget(request_group)
        
        container_widget.setLayout(container_layout)
        scroll_area.setWidget(container_widget)
        main_layout.addWidget(scroll_area)
        
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
        main_layout.addWidget(close_btn)
        
        self.setLayout(main_layout)