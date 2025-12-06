from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt
from datetime import datetime
from models.user_model import UserModel

class CustomerManagementPanel(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_model = UserModel(db)
        self.init_ui()
        self.load_customers()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Customer Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search customers...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        self.search_input.textChanged.connect(self.search_customers)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        layout.addSpacing(10)
        
        # Customers table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(7)
        self.customers_table.setHorizontalHeaderLabels([
            "ID", "Name", "Email", "Phone", "Address", "Joined", "Status"
        ])
        
        self.customers_table.setStyleSheet("""
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
        
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.customers_table)
        
        self.setLayout(layout)
    
    def load_customers(self):
        customers = self.user_model.get_all_users('customer')
        self.customers_table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            self.customers_table.setItem(row, 0, QTableWidgetItem(str(customer['id'])))
            self.customers_table.setItem(row, 1, QTableWidgetItem(f"{customer['first_name']} {customer['last_name']}"))
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer['email']))
            self.customers_table.setItem(row, 3, QTableWidgetItem(customer['phone'] or 'N/A'))
            self.customers_table.setItem(row, 4, QTableWidgetItem(customer['address'] or 'N/A'))
            
            join_date = customer['created_at'].strftime('%Y-%m-%d') if isinstance(customer['created_at'], datetime) else customer['created_at']
            self.customers_table.setItem(row, 5, QTableWidgetItem(join_date))
            
            status_item = QTableWidgetItem("Active" if customer['is_active'] else "Inactive")
            if customer['is_active']:
                status_item.setBackground(Qt.GlobalColor.green)
                status_item.setForeground(Qt.GlobalColor.white)
            else:
                status_item.setBackground(Qt.GlobalColor.red)
                status_item.setForeground(Qt.GlobalColor.white)
            self.customers_table.setItem(row, 6, status_item)
    
    def search_customers(self):
        search_text = self.search_input.text().lower()
        for row in range(self.customers_table.rowCount()):
            match = False
            for col in range(3):  # Check ID, Name, Email
                item = self.customers_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.customers_table.setRowHidden(row, not match)