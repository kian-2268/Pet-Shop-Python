from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QMessageBox, QHeaderView, QDialog,
                             QTextEdit, QGroupBox, QDateEdit, QScrollArea, 
                             QGridLayout)
from PyQt6.QtCore import Qt, QDateTime
from datetime import datetime
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
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Adoption Management")
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
        self.status_combo.addItems(["All", "Pending", "Approved", "Rejected"])
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
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Pet
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Species
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Request Date
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Notes
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Actions
        
        layout.addWidget(self.requests_table)
        
        self.setLayout(layout)
    
    def load_adoption_requests(self):
        requests = self.adoption_model.get_adoption_requests()
        self.display_requests(requests)
        self.update_stats(requests)
    
    def display_requests(self, requests):
        self.requests_table.setRowCount(len(requests))
        
        for row, request in enumerate(requests):
            self.requests_table.setItem(row, 0, QTableWidgetItem(str(request['id'])))
            self.requests_table.setItem(row, 1, QTableWidgetItem(f"{request['first_name']} {request['last_name']}"))
            self.requests_table.setItem(row, 2, QTableWidgetItem(request['pet_name']))
            self.requests_table.setItem(row, 3, QTableWidgetItem(request['species']))
            
            # Format date 
            request_date = request['request_date']
            if isinstance(request_date, str):
                request_date = datetime.strptime(request_date, '%Y-%m-%d %H:%M:%S')
            self.requests_table.setItem(row, 4, QTableWidgetItem(request_date.strftime('%Y-%m-%d %H:%M')))
            
            # Status with foreground color
            status_item = QTableWidgetItem(request['status'])
            if request['status'] == 'Pending':
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            elif request['status'] == 'Approved':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif request['status'] == 'Rejected':
                status_item.setForeground(Qt.GlobalColor.darkRed)
            self.requests_table.setItem(row, 5, status_item)
            
            # Notes - truncate if too long
            notes = request.get('notes', '')
            if len(notes) > 50:
                notes = notes[:50] + '...'
            self.requests_table.setItem(row, 6, QTableWidgetItem(notes))
            
            # Actions
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background-color: white;")
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
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
            view_btn.clicked.connect(lambda checked, r=request: self.view_request_details(r))
            actions_layout.addWidget(view_btn)
            
            if request['status'] == 'Pending':
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
                approve_btn.clicked.connect(lambda checked, r=request: self.update_request_status(r['id'], 'Approved'))
                actions_layout.addWidget(approve_btn)
                
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
                reject_btn.clicked.connect(lambda checked, r=request: self.update_request_status(r['id'], 'Rejected'))
                actions_layout.addWidget(reject_btn)
            
            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.requests_table.setCellWidget(row, 7, actions_widget)
    
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
                status_item = self.requests_table.item(row, 5)
                if status_item and status_item.text() == status:
                    self.requests_table.setRowHidden(row, False)
                else:
                    self.requests_table.setRowHidden(row, True)
    
    def apply_date_filter(self):
        start_date = self.start_date.date().toString('yyyy-MM-dd')
        end_date = self.end_date.date().toString('yyyy-MM-dd')
        
        all_requests = self.adoption_model.get_adoption_requests()
        filtered_requests = []
        
        for request in all_requests:
            request_date = request['request_date']
            if isinstance(request_date, str):
                request_date = datetime.strptime(request_date, '%Y-%m-%d %H:%M:%S')
            
            if start_date <= request_date.strftime('%Y-%m-%d') <= end_date:
                filtered_requests.append(request)
        
        self.display_requests(filtered_requests)
        self.update_stats(filtered_requests)
    
    def update_request_status(self, request_id, status):
        # Confirmation dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"Confirm Status Update")
        msg_box.setText(f"Are you sure you want to {status.lower()} this adoption request?")
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
            # For admin, use user_id 1 as approved_by
            if self.adoption_model.update_adoption_status(request_id, status, 1):
                if status == 'Approved':
                    # Update pet status to adopted
                    query = "UPDATE pets SET status = 'Adopted' WHERE id = (SELECT pet_id FROM adoption_requests WHERE id = %s)"
                    self.db.execute_query(query, (request_id,))
                
                # Success message
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText(f"Adoption request {status.lower()} successfully")
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
                self.load_adoption_requests()
            else:
                # Error message
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Error")
                error_msg.setText("Failed to update adoption request")
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
        customer_layout.addWidget(QLabel(f"{self.request['first_name']} {self.request['last_name']}"), 0, 1)
        
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
        
        # Get additional pet details
        pet = self.pet_model.get_pet_by_id(self.request['pet_id'])
        
        pet_layout.addWidget(QLabel("Pet Name:"), 0, 0)
        pet_layout.addWidget(QLabel(self.request['pet_name']), 0, 1)
        
        pet_layout.addWidget(QLabel("Species:"), 0, 2)
        pet_layout.addWidget(QLabel(self.request['species']), 0, 3)
        
        pet_layout.addWidget(QLabel("Breed:"), 1, 0)
        breed = pet['breed'] if pet and pet['breed'] else 'Mixed'
        pet_layout.addWidget(QLabel(breed), 1, 1)
        
        pet_layout.addWidget(QLabel("Age:"), 1, 2)
        age = str(pet['age']) if pet and pet['age'] else 'N/A'
        pet_layout.addWidget(QLabel(age), 1, 3)
        
        pet_layout.addWidget(QLabel("Gender:"), 2, 0)
        gender = pet['gender'] if pet and pet['gender'] else 'N/A'
        pet_layout.addWidget(QLabel(gender), 2, 1)
        
        pet_group.setLayout(pet_layout)
        container_layout.addWidget(pet_group)
        
        # Adoption Request Details Group
        request_group = QGroupBox("Adoption Request Details")
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
        request_layout.addWidget(status_label, 0, 3)
        
        request_layout.addWidget(QLabel("Customer Notes:"), 1, 0)
        notes_text = QTextEdit()
        notes_text.setPlainText(self.request.get('notes', 'No notes provided'))
        notes_text.setReadOnly(True)
        notes_text.setMaximumHeight(100)
        notes_text.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        request_layout.addWidget(notes_text, 1, 1, 1, 3)
        
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
