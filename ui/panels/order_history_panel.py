from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QDialogButtonBox, QGroupBox)
from PyQt6.QtCore import Qt
from models.order_model import OrderModel

class OrderHistoryPanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.order_model = OrderModel(db)
        self.init_ui()
        self.load_orders()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Order History")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"])
        self.status_combo.currentTextChanged.connect(self.filter_orders)
        
        filter_layout.addWidget(self.status_combo)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        layout.addSpacing(20)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels([
            "Order ID", "Date", "Items", "Total Amount", "Status", "Payment Method", "Actions"
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
        orders = self.order_model.get_orders_by_customer(self.user_id)
        self.orders_table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order['id'])))
            
            # Format date
            order_date = order['order_date']
            if isinstance(order_date, str):
                from datetime import datetime
                order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            self.orders_table.setItem(row, 1, QTableWidgetItem(order_date.strftime('%Y-%m-%d %H:%M')))
            
            # Get order items count
            items = self.order_model.get_order_details(order['id'])
            items_count = len(items)
            items_text = f"{items_count} item{'s' if items_count != 1 else ''}"
            self.orders_table.setItem(row, 2, QTableWidgetItem(items_text))
            
            self.orders_table.setItem(row, 3, QTableWidgetItem(f"${float(order['total_amount']):.2f}"))
            
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
            self.orders_table.setItem(row, 4, status_item)
            
            self.orders_table.setItem(row, 5, QTableWidgetItem(order.get('payment_method', 'N/A')))
            
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
            view_btn.clicked.connect(lambda checked, o=order: self.view_order_details(o))
            actions_layout.addWidget(view_btn)
            
            if order['status'] in ['Pending', 'Confirmed']:
                cancel_btn = QPushButton("Cancel Order")
                cancel_btn.setStyleSheet("""
                    QPushButton {
                        background: #e74c3c;
                        color: white;
                        padding: 5px 10px;
                        border: none;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background: #c0392b;
                    }
                """)
                cancel_btn.clicked.connect(lambda checked, o=order: self.cancel_order(o['id']))
                actions_layout.addWidget(cancel_btn)
            
            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.orders_table.setCellWidget(row, 6, actions_widget)
    
    def filter_orders(self, status):
        if status == "All":
            for row in range(self.orders_table.rowCount()):
                self.orders_table.setRowHidden(row, False)
        else:
            for row in range(self.orders_table.rowCount()):
                status_item = self.orders_table.item(row, 4)
                if status_item and status_item.text() == status:
                    self.orders_table.setRowHidden(row, False)
                else:
                    self.orders_table.setRowHidden(row, True)
    
    def view_order_details(self, order):
        dialog = CustomerOrderDetailsDialog(order, self.order_model)
        dialog.exec()
    
    def cancel_order(self, order_id):
        reply = QMessageBox.question(self, "Cancel Order", 
                                   "Are you sure you want to cancel this order?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            query = "UPDATE orders SET status = 'Cancelled' WHERE id = %s"
            if self.db.execute_query(query, (order_id,)):
                QMessageBox.information(self, "Success", "Order cancelled successfully")
                self.load_orders()
            else:
                QMessageBox.warning(self, "Error", "Failed to cancel order")

class CustomerOrderDetailsDialog(QDialog):
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
        items_table.setColumnCount(5)
        items_table.setHorizontalHeaderLabels(["Item", "Type", "Quantity", "Unit Price", "Total"])
        
        order_items = self.order_model.get_order_details(self.order['id'])
        items_table.setRowCount(len(order_items))
        
        total_amount = 0
        for row, item in enumerate(order_items):
            items_table.setItem(row, 0, QTableWidgetItem(item['item_name']))
            items_table.setItem(row, 1, QTableWidgetItem(item['item_type'].title()))
            items_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            items_table.setItem(row, 3, QTableWidgetItem(f"${float(item['unit_price']):.2f}"))
            
            item_total = float(item['unit_price']) * item['quantity']
            items_table.setItem(row, 4, QTableWidgetItem(f"${item_total:.2f}"))
            total_amount += item_total
        
        items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        items_layout.addWidget(items_table)
        
        # Order totals
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        totals_layout.addWidget(QLabel(f"Subtotal: ${total_amount:.2f}"))
        totals_layout.addWidget(QLabel(f"Tax (8%): ${total_amount * 0.08:.2f}"))
        totals_layout.addWidget(QLabel(f"Total: ${total_amount * 1.08:.2f}"))
        items_layout.addLayout(totals_layout)
        
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