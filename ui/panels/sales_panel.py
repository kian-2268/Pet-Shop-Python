from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QMessageBox, QHeaderView,
                             QGroupBox, QLineEdit, QFormLayout, QDialog)
from PyQt6.QtCore import QDateTime, Qt
from datetime import datetime, timedelta
from models.order_model import OrderModel
from models.user_model import UserModel

class SalesPanel(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.order_model = OrderModel(db)
        self.user_model = UserModel(db)
        self.init_ui()
        self.load_orders()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Sales Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Filters
        filters_layout = QHBoxLayout()
        
        filters_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"])
        self.status_combo.currentTextChanged.connect(self.filter_orders)
        
        filters_layout.addWidget(self.status_combo)
        
        filters_layout.addWidget(QLabel("Date From:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDateTime.currentDateTime().date().addDays(-30))
        self.start_date.setCalendarPopup(True)
        
        filters_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDateTime.currentDateTime().date())
        self.end_date.setCalendarPopup(True)
        
        filters_layout.addWidget(self.start_date)
        filters_layout.addWidget(self.end_date)
        
        apply_btn = QPushButton("Apply Filter")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        apply_btn.clicked.connect(self.apply_date_filter)
        
        filters_layout.addWidget(apply_btn)
        filters_layout.addStretch()
        
        layout.addLayout(filters_layout)
        layout.addSpacing(20)
        
        # Quick stats
        stats_layout = QHBoxLayout()
        
        self.total_sales_label = QLabel("Total Sales: $0.00")
        self.total_sales_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
        
        self.total_orders_label = QLabel("Total Orders: 0")
        self.total_orders_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        
        self.pending_orders_label = QLabel("Pending Orders: 0")
        self.pending_orders_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f39c12;")
        
        stats_layout.addWidget(self.total_sales_label)
        stats_layout.addWidget(self.total_orders_label)
        stats_layout.addWidget(self.pending_orders_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        layout.addSpacing(20)
        
        # Orders table
        self.orders_table = QTableWidget()
        if self.user_role == 'admin':
            self.orders_table.setColumnCount(9)
            self.orders_table.setHorizontalHeaderLabels([
                "Order ID", "Customer", "Date", "Items", "Amount", "Status", "Payment", "Staff", "Actions"
            ])
        else:
            self.orders_table.setColumnCount(8)
            self.orders_table.setHorizontalHeaderLabels([
                "Order ID", "Customer", "Date", "Items", "Amount", "Status", "Payment", "Actions"
            ])
        
        self.orders_table.setStyleSheet("""
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
        
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.orders_table)
        
        self.setLayout(layout)
    
    def load_orders(self):
        orders = self.order_model.get_all_orders()
        self.display_orders(orders)
        self.update_stats(orders)
    
    def display_orders(self, orders):
        self.orders_table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order['id'])))
            self.orders_table.setItem(row, 1, QTableWidgetItem(order.get('customer_name', 'N/A')))
            
            # Format date
            order_date = order['order_date']
            if isinstance(order_date, str):
                order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            self.orders_table.setItem(row, 2, QTableWidgetItem(order_date.strftime('%Y-%m-%d %H:%M')))
            
            # Get order items count
            items = self.order_model.get_order_details(order['id'])
            items_count = len(items)
            items_text = f"{items_count} item{'s' if items_count != 1 else ''}"
            self.orders_table.setItem(row, 3, QTableWidgetItem(items_text))
            
            self.orders_table.setItem(row, 4, QTableWidgetItem(f"${float(order['total_amount']):.2f}"))
            
            # Status with color coding
            status_item = QTableWidgetItem(order['status'])
            if order['status'] == 'Pending':
                status_item.setBackground(Qt.GlobalColor.yellow)
            elif order['status'] == 'Confirmed':
                status_item.setBackground(Qt.GlobalColor.blue)
                status_item.setForeground(Qt.GlobalColor.white)
            elif order['status'] == 'Shipped':
                status_item.setBackground(Qt.GlobalColor.cyan)
            elif order['status'] == 'Delivered':
                status_item.setBackground(Qt.GlobalColor.green)
                status_item.setForeground(Qt.GlobalColor.white)
            elif order['status'] == 'Cancelled':
                status_item.setBackground(Qt.GlobalColor.red)
                status_item.setForeground(Qt.GlobalColor.white)
            self.orders_table.setItem(row, 5, status_item)
            
            self.orders_table.setItem(row, 6, QTableWidgetItem(order.get('payment_method', 'N/A')))
            
            col_offset = 0
            if self.user_role == 'admin':
                staff_name = f"{order['first_name']} {order['last_name']}" if order['first_name'] else "Not Assigned"
                self.orders_table.setItem(row, 7, QTableWidgetItem(staff_name))
                col_offset = 1
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            view_btn = QPushButton("View")
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
            view_btn.clicked.connect(lambda checked, o=order: self.view_order_details(o))
            actions_layout.addWidget(view_btn)
            
            if order['status'] == 'Pending':
                confirm_btn = QPushButton("Confirm")
                confirm_btn.setStyleSheet("""
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
                confirm_btn.clicked.connect(lambda checked, o=order: self.update_order_status(o['id'], 'Confirmed'))
                actions_layout.addWidget(confirm_btn)
            
            if order['status'] in ['Confirmed', 'Shipped']:
                next_status = 'Shipped' if order['status'] == 'Confirmed' else 'Delivered'
                status_btn = QPushButton(next_status)
                status_btn.setStyleSheet("""
                    QPushButton {
                        background: #17a2b8;
                        color: white;
                        padding: 5px 10px;
                        border: none;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background: #138496;
                    }
                """)
                status_btn.clicked.connect(lambda checked, o=order, s=next_status: self.update_order_status(o['id'], s))
                actions_layout.addWidget(status_btn)
            
            if order['status'] in ['Pending', 'Confirmed']:
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
                cancel_btn.clicked.connect(lambda checked, o=order: self.update_order_status(o['id'], 'Cancelled'))
                actions_layout.addWidget(cancel_btn)
            
            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.orders_table.setCellWidget(row, 7 + col_offset, actions_widget)
    
    def update_stats(self, orders):
        total_sales = sum(float(order['total_amount']) for order in orders)
        total_orders = len(orders)
        pending_orders = sum(1 for order in orders if order['status'] == 'Pending')
        
        self.total_sales_label.setText(f"Total Sales: ${total_sales:,.2f}")
        self.total_orders_label.setText(f"Total Orders: {total_orders}")
        self.pending_orders_label.setText(f"Pending Orders: {pending_orders}")
    
    def filter_orders(self, status):
        if status == "All":
            for row in range(self.orders_table.rowCount()):
                self.orders_table.setRowHidden(row, False)
        else:
            for row in range(self.orders_table.rowCount()):
                status_item = self.orders_table.item(row, 5)
                if status_item and status_item.text() == status:
                    self.orders_table.setRowHidden(row, False)
                else:
                    self.orders_table.setRowHidden(row, True)
    
    def apply_date_filter(self):
        start_date = self.start_date.date().toString('yyyy-MM-dd')
        end_date = self.end_date.date().toString('yyyy-MM-dd')
        
        all_orders = self.order_model.get_all_orders()
        filtered_orders = []
        
        for order in all_orders:
            order_date = order['order_date']
            if isinstance(order_date, str):
                order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            
            if start_date <= order_date.strftime('%Y-%m-%d') <= end_date:
                filtered_orders.append(order)
        
        self.display_orders(filtered_orders)
        self.update_stats(filtered_orders)
    
    def view_order_details(self, order):
        dialog = OrderDetailsDialog(order, self.order_model)
        dialog.exec()
    
    def update_order_status(self, order_id, new_status):
        query = "UPDATE orders SET status = %s WHERE id = %s"
        if self.db.execute_query(query, (new_status, order_id)):
            QMessageBox.information(self, "Success", f"Order status updated to {new_status}")
            self.load_orders()
        else:
            QMessageBox.warning(self, "Error", "Failed to update order status")

class OrderDetailsDialog(QDialog):
    def __init__(self, order, order_model):
        super().__init__()
        self.order = order
        self.order_model = order_model
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Order Details - #{self.order['id']}")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout()
        
        # Order info
        info_group = QGroupBox("Order Information")
        info_layout = QFormLayout()
        
        info_layout.addRow("Order ID:", QLabel(str(self.order['id'])))
        info_layout.addRow("Customer:", QLabel(self.order.get('customer_name', 'N/A')))
        info_layout.addRow("Order Date:", QLabel(str(self.order['order_date'])))
        info_layout.addRow("Total Amount:", QLabel(f"${float(self.order['total_amount']):.2f}"))
        info_layout.addRow("Status:", QLabel(self.order['status']))
        info_layout.addRow("Payment Method:", QLabel(self.order.get('payment_method', 'N/A')))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Order items
        items_group = QGroupBox("Order Items")
        items_layout = QVBoxLayout()
        
        items_table = QTableWidget()
        items_table.setColumnCount(4)
        items_table.setHorizontalHeaderLabels(["Item", "Type", "Quantity", "Price"])
        
        order_items = self.order_model.get_order_details(self.order['id'])
        items_table.setRowCount(len(order_items))
        
        for row, item in enumerate(order_items):
            items_table.setItem(row, 0, QTableWidgetItem(item['item_name']))
            items_table.setItem(row, 1, QTableWidgetItem(item['item_type'].title()))
            items_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            items_table.setItem(row, 3, QTableWidgetItem(f"${float(item['unit_price']):.2f}"))
        
        items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        items_layout.addWidget(items_table)
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
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