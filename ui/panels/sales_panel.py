from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QMessageBox, QHeaderView,
                             QGroupBox, QDialog, QGridLayout, QScrollArea)
from PyQt6.QtCore import QDateTime, Qt
from datetime import datetime
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
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Sales Management")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Filters
        filter_layout = QHBoxLayout()
        
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
        self.status_combo.addItems(["All", "Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"])
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
        self.status_combo.currentTextChanged.connect(self.filter_orders)
        filter_layout.addWidget(self.status_combo)
        
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
        
        self.total_sales_label = QLabel("Total Sales: ₱0.00")
        self.total_sales_label.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                color: #27ae60;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        
        self.total_orders_label = QLabel("Total Orders: 0")
        self.total_orders_label.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                color: #3498db;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        
        self.pending_orders_label = QLabel("Pending Orders: 0")
        self.pending_orders_label.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                color: #f39c12;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        
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
        
        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        if self.user_role == 'admin':
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        else:
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.orders_table)
        
        self.setLayout(layout)
    
    def load_orders(self):
        orders = self.order_model.get_all_orders()
        self.display_orders(orders)
        self.update_stats(orders)
    
    def display_orders(self, orders):
        self.orders_table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            # Order ID
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order['id'])))
            
            # Customer Name 
            customer_id = order.get('customer_id')
            customer_name = 'N/A'
            if customer_id:
                # Check if customer name is in order data
                if 'customer_name' in order:
                    customer_name = order['customer_name']
                elif 'customer_first_name' in order and 'customer_last_name' in order:
                    customer_name = f"{order.get('customer_first_name', '')} {order.get('customer_last_name', '')}".strip()
                else:
                    # Fetch from database
                    customer = self.user_model.get_user_by_id(customer_id)
                    if customer:
                        customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                        if not customer_name.strip():
                            customer_name = customer.get('email', 'N/A')
            self.orders_table.setItem(row, 1, QTableWidgetItem(customer_name))
            
            # Date
            order_date = order['order_date']
            if isinstance(order_date, str):
                order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            self.orders_table.setItem(row, 2, QTableWidgetItem(order_date.strftime('%Y-%m-%d %H:%M')))
            
            # Items count
            items = self.order_model.get_order_details(order['id'])
            items_count = len(items)
            items_text = f"{items_count} item{'s' if items_count != 1 else ''}"
            self.orders_table.setItem(row, 3, QTableWidgetItem(items_text))
            
            # Amount
            self.orders_table.setItem(row, 4, QTableWidgetItem(f"₱{float(order['total_amount']):.2f}"))
            
            # Status
            status_item = QTableWidgetItem(order['status'])
            if order['status'] == 'Pending':
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            elif order['status'] == 'Confirmed':
                status_item.setForeground(Qt.GlobalColor.darkBlue)
            elif order['status'] == 'Shipped':
                status_item.setForeground(Qt.GlobalColor.darkCyan)
            elif order['status'] == 'Delivered':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif order['status'] == 'Cancelled':
                status_item.setForeground(Qt.GlobalColor.darkRed)
            self.orders_table.setItem(row, 5, status_item)
            
            # Payment Method
            self.orders_table.setItem(row, 6, QTableWidgetItem(order.get('payment_method', 'N/A')))
            
            col_offset = 0
            if self.user_role == 'admin':
                # Staff Name 
                staff_id = order.get('staff_id')
                staff_name = "Not Assigned"
                if staff_id:
                    staff = self.user_model.get_user_by_id(staff_id)
                    if staff:
                        staff_name = f"{staff.get('first_name', '')} {staff.get('last_name', '')}".strip()
                        if not staff_name.strip():
                            staff_name = staff.get('email', 'Not Assigned')
                
                self.orders_table.setItem(row, 7, QTableWidgetItem(staff_name))
                col_offset = 1
            
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
            view_btn.clicked.connect(lambda checked, o=order: self.view_order_details(o))
            actions_layout.addWidget(view_btn)
            
            if order['status'] == 'Pending':
                confirm_btn = QPushButton("Confirm")
                confirm_btn.setMinimumHeight(20)
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
                status_btn.setMinimumHeight(20)
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
                cancel_btn.clicked.connect(lambda checked, o=order: self.update_order_status(o['id'], 'Cancelled'))
                actions_layout.addWidget(cancel_btn)
            
            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.orders_table.setCellWidget(row, 7 + col_offset, actions_widget)
    
    def update_stats(self, orders):
        total_sales = sum(float(order['total_amount']) for order in orders)
        total_orders = len(orders)
        pending_orders = sum(1 for order in orders if order['status'] == 'Pending')
        
        self.total_sales_label.setText(f"Total Sales: ₱{total_sales:,.2f}")
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
        dialog = OrderDetailsDialog(order, self.order_model, self.user_model)
        dialog.exec()
    
    def update_order_status(self, order_id, new_status):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"Confirm Status Update")
        msg_box.setText(f"Are you sure you want to change the order status to '{new_status}'?")
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
            query = "UPDATE orders SET status = %s WHERE id = %s"
            if self.db.execute_query(query, (new_status, order_id)):
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText(f"Order status updated to {new_status}")
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
                self.load_orders()
            else:
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Error")
                error_msg.setText("Failed to update order status")
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
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                error_msg.exec()


class OrderDetailsDialog(QDialog):
    def __init__(self, order, order_model, user_model=None):
        super().__init__()
        self.order = order
        self.order_model = order_model
        self.user_model = user_model
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Order Details - #{self.order['id']}")
        self.setModal(True)
        self.setStyleSheet("background-color: white; color: black;")
        self.resize(700, 500)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
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
        
        container_widget = QWidget()
        container_widget.setStyleSheet("background-color: white;")
        container_layout = QVBoxLayout()
        container_layout.setSpacing(20)
        
        # Order Information Group
        info_group = QGroupBox("Order Information")
        info_group.setStyleSheet("""
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
        info_layout = QGridLayout()
        info_layout.setHorizontalSpacing(20)
        info_layout.setVerticalSpacing(10)
        
        info_layout.addWidget(QLabel("Order ID:"), 0, 0)
        info_layout.addWidget(QLabel(str(self.order['id'])), 0, 1)
        
        # Customer Name 
        customer_id = self.order.get('customer_id')
        customer_name = 'N/A'
        if customer_id and self.user_model:
            customer = self.user_model.get_user_by_id(customer_id)
            if customer:
                customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                if not customer_name.strip():
                    customer_name = customer.get('email', 'N/A')
        elif 'customer_name' in self.order:
            customer_name = self.order['customer_name']
        
        info_layout.addWidget(QLabel("Customer:"), 0, 2)
        info_layout.addWidget(QLabel(customer_name), 0, 3)
        
        info_layout.addWidget(QLabel("Order Date:"), 1, 0)
        order_date = self.order['order_date']
        if isinstance(order_date, str):
            order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
        info_layout.addWidget(QLabel(order_date.strftime('%Y-%m-%d %H:%M')), 1, 1)
        
        info_layout.addWidget(QLabel("Total Amount:"), 1, 2)
        info_layout.addWidget(QLabel(f"₱{float(self.order['total_amount']):.2f}"), 1, 3)
        
        info_layout.addWidget(QLabel("Status:"), 2, 0)
        status_label = QLabel(self.order['status'])
        if self.order['status'] == 'Pending':
            status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        elif self.order['status'] == 'Confirmed':
            status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        elif self.order['status'] == 'Shipped':
            status_label.setStyleSheet("color: #3498db; font-weight: bold;")
        elif self.order['status'] == 'Delivered':
            status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        elif self.order['status'] == 'Cancelled':
            status_label.setStyleSheet("color: #9e9e9e; font-weight: bold; font-style: italic;")
        info_layout.addWidget(status_label, 2, 1)
        
        info_layout.addWidget(QLabel("Payment Method:"), 2, 2)
        info_layout.addWidget(QLabel(self.order.get('payment_method', 'N/A')), 2, 3)
        
        info_group.setLayout(info_layout)
        container_layout.addWidget(info_group)
        
        # Order items group
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
                color: black;
            }
        """)
        items_layout = QVBoxLayout()
        
        items_table = QTableWidget()
        items_table.setColumnCount(5)
        items_table.setHorizontalHeaderLabels(["Item", "Type", "Quantity", "Unit Price", "Subtotal"])
        
        items_table.setStyleSheet("""
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
        
        order_items = self.order_model.get_order_details(self.order['id'])
        items_table.setRowCount(len(order_items))
        
        total_items_value = 0
        for row, item in enumerate(order_items):
            items_table.setItem(row, 0, QTableWidgetItem(item['item_name']))
            items_table.setItem(row, 1, QTableWidgetItem(item['item_type'].title()))
            items_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            unit_price = float(item['unit_price'])
            items_table.setItem(row, 3, QTableWidgetItem(f"₱{unit_price:.2f}"))
            
            subtotal = unit_price * item['quantity']
            total_items_value += subtotal
            items_table.setItem(row, 4, QTableWidgetItem(f"₱{subtotal:.2f}"))
        
        items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        items_layout.addWidget(items_table)
        
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_label = QLabel(f"Total Items Value: ₱{total_items_value:.2f}")
        total_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #27ae60;")
        total_layout.addWidget(total_label)
        items_layout.addLayout(total_layout)
        
        items_group.setLayout(items_layout)
        container_layout.addWidget(items_group)
        
        container_widget.setLayout(container_layout)
        scroll_area.setWidget(container_widget)
        main_layout.addWidget(scroll_area)
        
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
