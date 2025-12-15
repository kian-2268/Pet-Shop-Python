from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from models.order_model import OrderModel

class OrderHistoryPanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.order_model = OrderModel(db)
        self.init_ui()
        QTimer.singleShot(0, self.load_orders)
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Order History")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        layout.addWidget(title)
        
        # Filters
        filter_layout = QHBoxLayout()

        # Label with white background
        status_label = QLabel("Status:")
        status_label.setStyleSheet("""
            QLabel {    
                background-color: #f9fafb;
                color: black;
                padding: 5px 10px;
            }
        """)
        filter_layout.addWidget(status_label)

        # Combo box with white background
        self.status_combo = QComboBox()
        self.status_combo.setStyleSheet("""
            QComboBox {
                color: black;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
            }
        """)
        self.status_combo.addItems(["All", "Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"])
        self.status_combo.currentTextChanged.connect(self.filter_orders)
        filter_layout.addWidget(self.status_combo)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        layout.addSpacing(10)
        
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
        
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.orders_table)
        
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
        refresh_btn.clicked.connect(self.refresh_orders)  # Connect to new method
        layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
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
            
            self.orders_table.setItem(row, 3, QTableWidgetItem(f"₱{float(order['total_amount']):.2f}"))
            
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
            
            # Actions column (index 6)
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background-color: white;")
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(10)
            
            # View Details button
            view_btn = QPushButton("Details")
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
            view_btn.clicked.connect(lambda checked, o=order: self.view_order_details(o))
            actions_layout.addWidget(view_btn)
            
            # Cancel button or status label
            if order['status'] in ['Pending', 'Confirmed']:
                cancel_btn = QPushButton("Cancel")
                cancel_btn.setMinimumHeight(20)
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
                cancel_btn.clicked.connect(lambda checked, oid=order['id']: self.cancel_order(oid))
                actions_layout.addWidget(cancel_btn)
            elif order['status'] == 'Cancelled':
                # Show a label for cancelled orders
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
            self.orders_table.setCellWidget(row, 6, actions_widget)
    
    def refresh_orders(self):
        QTimer.singleShot(0, self.load_orders)
    
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
        # Question dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Cancel Order")
        msg_box.setText("Are you sure you want to cancel this order?")
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
            query = "UPDATE orders SET status = 'Cancelled' WHERE id = %s"
            if self.db.execute_query(query, (order_id,)):
                # Success message
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText("Order cancelled successfully")
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
                self.refresh_orders()  # Changed from self.load_orders() to self.refresh_orders()
            else:
                # Error message
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Error")
                error_msg.setText("Failed to cancel order")
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


class CustomerOrderDetailsDialog(QDialog):
    def __init__(self, order, order_model):
        super().__init__()
        self.order = order
        self.order_model = order_model
        self.setStyleSheet("background-color: white; color: black;")
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Order Details - #{self.order['id']}")
        self.setModal(True)
        self.resize(600, 550)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Order information group box
        order_group = QGroupBox("Order Information")
        order_group.setStyleSheet("""
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
        order_layout = QFormLayout()
        
        # Format date
        order_date = self.order['order_date']
        if isinstance(order_date, str):
            from datetime import datetime
            order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            date_str = order_date.strftime('%B %d, %Y at %I:%M %p')
        else:
            date_str = str(order_date)
        
        order_layout.addRow("Order ID:", QLabel(str(self.order['id'])))
        order_layout.addRow("Order Date:", QLabel(date_str))
        order_layout.addRow("Payment Method:", QLabel(self.order.get('payment_method', 'N/A')))
        
        order_group.setLayout(order_layout)
        layout.addWidget(order_group)
        
        # Order status group box
        status_group = QGroupBox("Order Status")
        status_group.setStyleSheet("""
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
        status_layout = QFormLayout()
        
        # Status with colored label
        status_label = QLabel(self.order['status'])
        if self.order['status'] == 'Pending':
            status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        elif self.order['status'] == 'Confirmed':
            status_label.setStyleSheet("color: #3498db; font-weight: bold;")
        elif self.order['status'] == 'Completed':
            status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        elif self.order['status'] == 'Shipped':
            status_label.setStyleSheet("color: #9b59b6; font-weight: bold;")
        elif self.order['status'] == 'Delivered':
            status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        elif self.order['status'] == 'Cancelled':
            status_label.setStyleSheet("color: #9e9e9e; font-weight: bold; font-style: italic;")
        elif self.order['status'] == 'Refunded':
            status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        status_layout.addRow("Status:", status_label)
        status_layout.addRow("Total Amount:", QLabel(f"₱{float(self.order['total_amount']):.2f}"))
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Order items group box
        items_group = QGroupBox("Order Items")
        items_group.setStyleSheet("""
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
        items_layout = QVBoxLayout()
        
        items_table = QTableWidget()
        items_table.setColumnCount(5)
        items_table.setHorizontalHeaderLabels(["Item", "Type", "Quantity", "Unit Price", "Total"])
        
        items_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                background: white;
            }
            QHeaderView::section {
                background: #f8f9fa;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: black;
            }
        """)
        
        order_items = self.order_model.get_order_details(self.order['id'])
        items_table.setRowCount(len(order_items))
        
        item_subtotal = 0
        for row, item in enumerate(order_items):
            items_table.setItem(row, 0, QTableWidgetItem(item['item_name']))
            items_table.setItem(row, 1, QTableWidgetItem(item['item_type'].title()))
            items_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            items_table.setItem(row, 3, QTableWidgetItem(f"₱{float(item['unit_price']):.2f}"))
            
            item_total = float(item['unit_price']) * item['quantity']
            items_table.setItem(row, 4, QTableWidgetItem(f"₱{item_total:.2f}"))
            item_subtotal += item_total
        
        items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        items_layout.addWidget(items_table)
        
        # Order totals - Calculate actual tax from database total
        db_total = float(self.order['total_amount'])
        
        # Calculate actual tax (not assuming 12%)
        # tax = database_total - sum_of_items
        actual_tax = db_total - item_subtotal
        
        # Calculate tax rate for display
        if item_subtotal > 0:
            tax_rate_percent = (actual_tax / item_subtotal) * 100
        else:
            tax_rate_percent = 0
        
        totals_container = QWidget()
        totals_container.setStyleSheet("""
            QWidget {
                background-color: #f9d162;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
        """)
        totals_layout = QHBoxLayout()
        
        totals_text = QLabel(f"""
            <b>Subtotal:</b> ₱{item_subtotal:.2f}<br>
            <b>Tax ({tax_rate_percent:.1f}%):</b> ₱{actual_tax:.2f}<br>
            <b style='font-size: 14px;'>Total:</b> <span style='color: #e74c3c; font-size: 16px; font-weight: bold;'>₱{db_total:.2f}</span>
        """)
        totals_text.setTextFormat(Qt.TextFormat.RichText)
        
        totals_layout.addWidget(totals_text)
        totals_layout.addStretch()
        
        totals_container.setLayout(totals_layout)
        items_layout.addWidget(totals_container)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
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
