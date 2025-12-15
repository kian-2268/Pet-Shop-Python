from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QGroupBox, QSpinBox,
                             QDialog, QDialogButtonBox, QFormLayout, QComboBox,
                             QTextEdit, QScrollArea, QVBoxLayout)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QTextDocument, QPageSize, QPageLayout
from decimal import Decimal
from models.cart_model import CartModel
from models.order_model import OrderModel
from models.user_model import UserModel
import os

class CartPanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.cart_model = CartModel(db)
        self.order_model = OrderModel(db)
        self.user_model = UserModel(db)
        self.init_ui()
        QTimer.singleShot(0, self.load_cart) 
    
    def init_ui(self):
        self.setStyleSheet("background-color: white; color: black;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        title = QLabel("My Shopping Cart")
        title.setStyleSheet("""
            background-color: white;
            font-size: 25px; 
            font-weight: bold; 
            color: black;
            padding: 10px 0;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addWidget(header_widget)
        
        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Type", "Price", "Quantity", "Total", "Actions"])
        self.cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.cart_table.setStyleSheet("""
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
        
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.cart_table)
        
        # Order Summary
        summary_group = QGroupBox("Order Summary")
        summary_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: black;
            }
        """)
        
        summary_layout = QVBoxLayout()
        
        # Totals
        totals_widget = QWidget()
        totals_layout = QVBoxLayout(totals_widget)
        
        # Subtotal
        subtotal_widget = QWidget()
        subtotal_layout = QHBoxLayout(subtotal_widget)
        subtotal_label = QLabel("Subtotal:")
        subtotal_label.setStyleSheet("color: black;")
        subtotal_layout.addWidget(subtotal_label)
        self.subtotal_label = QLabel("₱0.00")
        self.subtotal_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        subtotal_layout.addStretch()
        subtotal_layout.addWidget(self.subtotal_label)
        totals_layout.addWidget(subtotal_widget)
        
        # Tax
        tax_widget = QWidget()
        tax_layout = QHBoxLayout(tax_widget)
        tax_label = QLabel("Tax (12%):")
        tax_label.setStyleSheet("color: black;")
        tax_layout.addWidget(tax_label)
        self.tax_label = QLabel("₱0.00")
        self.tax_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        tax_layout.addStretch()
        tax_layout.addWidget(self.tax_label)
        totals_layout.addWidget(tax_widget)
        
        # Total
        total_widget = QWidget()
        total_layout = QHBoxLayout(total_widget)
        total_text_label = QLabel("Total:")
        total_text_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        total_layout.addWidget(total_text_label)
        self.total_label = QLabel("₱0.00")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e74c3c;")
        total_layout.addStretch()
        total_layout.addWidget(self.total_label)
        totals_layout.addWidget(total_widget)
        
        summary_layout.addWidget(totals_widget)
        
        # Checkout button
        self.checkout_btn = QPushButton("Proceed to Checkout")
        self.checkout_btn.setStyleSheet("""
            QPushButton {
                background: #5ab9ea;
                color: white;
                padding: 15px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: #78d1ff;
            }
            QPushButton:disabled {
                background: #95a5a6;
            }
        """)
        self.checkout_btn.clicked.connect(self.checkout)
        summary_layout.addWidget(self.checkout_btn)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        self.setLayout(layout)
    
    def load_cart(self):
        cart_items = self.cart_model.get_cart_items(self.user_id)
        self.cart_table.setRowCount(len(cart_items))
        
        subtotal = Decimal('0.00')
        
        for row, item in enumerate(cart_items):
            if 'item_name' not in item:
                item['item_name'] = 'Unknown Item'
            if 'item_type' not in item:
                item['item_type'] = 'product'
            if 'price' not in item:
                item['price'] = Decimal('0.00')
            if 'quantity' not in item:
                item['quantity'] = 1
            
            # Item name
            name_item = QTableWidgetItem(str(item['item_name']))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.cart_table.setItem(row, 0, name_item)
            
            # Item type
            type_item = QTableWidgetItem(str(item['item_type']).title())
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.cart_table.setItem(row, 1, type_item)
            
            # Price
            price_item = QTableWidgetItem(f"₱{float(item['price']):.2f}")
            price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.cart_table.setItem(row, 2, price_item)
            
            # Quantity widget with spin box
            quantity_widget = QWidget()
            quantity_widget.setStyleSheet("background-color: white; color:black;")
            quantity_layout = QHBoxLayout(quantity_widget)
            quantity_layout.setContentsMargins(0, 0, 0, 0)
            
            quantity_spin = QSpinBox()
            quantity_spin.setRange(1, 10 if item['item_type'] == 'product' else 1)
            quantity_spin.setValue(int(item['quantity']))
            quantity_spin.valueChanged.connect(lambda value, item_id=item['id']: self.update_quantity(item_id, value))
            
            quantity_layout.addWidget(quantity_spin)
            self.cart_table.setCellWidget(row, 3, quantity_widget)
            
            # Total
            item_total = Decimal(str(item['price'])) * Decimal(str(item['quantity']))
            total_item = QTableWidgetItem(f"₱{float(item_total):.2f}")
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.cart_table.setItem(row, 4, total_item)
            
            subtotal += item_total
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet("""
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
            remove_btn.clicked.connect(lambda checked, item_id=item['id']: self.remove_item(item_id))
            self.cart_table.setCellWidget(row, 5, remove_btn)
        
        tax = subtotal * Decimal('0.12')
        total = subtotal + tax
        
        self.subtotal_label.setText(f"₱{float(subtotal):.2f}")
        self.tax_label.setText(f"₱{float(tax):.2f}")
        self.total_label.setText(f"₱{float(total):.2f}")
        
        self.checkout_btn.setEnabled(len(cart_items) > 0)
    
    def update_quantity(self, cart_id, quantity):
        if self.cart_model.update_cart_quantity(cart_id, quantity):
            QTimer.singleShot(0, self.load_cart)  
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("Failed to update quantity")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet("""
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
            msg.exec()
    
    def remove_item(self, cart_id):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Remove Item")
        msg_box.setText("Are you sure you want to remove this item from your cart?")
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
            if self.cart_model.remove_from_cart(cart_id):
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText("Item removed from cart")
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
                QTimer.singleShot(0, self.load_cart)
            else:
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Error")
                error_msg.setText("Failed to remove item")
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
    
    def checkout(self):
        cart_items = self.cart_model.get_cart_items(self.user_id)
        if not cart_items:
            msg = QMessageBox(self)
            msg.setWindowTitle("Empty Cart")
            msg.setText("Your cart is empty")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet("""
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
            msg.exec()
            return
        
        # Get user info for checkout
        user_info = self.user_model.get_user_by_id(self.user_id)
        if not user_info:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("Could not retrieve user information")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()
            return
        
        # Show checkout dialog
        dialog = CheckoutDialog(cart_items, user_info, self.order_model, self.cart_model, self.user_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QTimer.singleShot(0, self.load_cart)
    
    def refresh_cart(self):
        QTimer.singleShot(0, self.load_cart)


class CheckoutDialog(QDialog):
    def __init__(self, cart_items, user_info, order_model, cart_model, user_id):
        super().__init__()
        self.cart_items = cart_items
        self.user_info = user_info
        self.order_model = order_model
        self.cart_model = cart_model
        self.user_id = user_id
        self.order_id = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Checkout")
        self.setModal(True)
        self.resize(600, 700)
        self.setStyleSheet("background-color: white; color: black;")
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create scroll area
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
        
        # Create container widget
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setSpacing(15)
        
        # Customer Information
        customer_group = QGroupBox("Customer Information")
        customer_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                margin-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: black;
            }
        """)
        
        customer_layout = QVBoxLayout(customer_group)
        
        # Customer name
        name_widget = QWidget()
        name_layout = QHBoxLayout(name_widget)
        name_label = QLabel(f"Name: {self.user_info.get('first_name', '')} {self.user_info.get('last_name', '')}")
        name_label.setStyleSheet("font-size: 14px; color: black;")
        name_layout.addWidget(name_label)
        customer_layout.addWidget(name_widget)
        
        # Customer email
        email_widget = QWidget()
        email_layout = QHBoxLayout(email_widget)
        email_label = QLabel(f"Email: {self.user_info.get('email', 'Not provided')}")
        email_label.setStyleSheet("font-size: 14px; color: black;")
        email_layout.addWidget(email_label)
        customer_layout.addWidget(email_widget)
        
        # Shipping Address
        address_widget = QWidget()
        address_layout = QVBoxLayout(address_widget)
        address_label = QLabel("Shipping Address *:")
        address_label.setStyleSheet("font-size: 14px; font-weight: bold; color: black;")
        address_layout.addWidget(address_label)
        
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Enter your complete shipping address")
        self.address_input.setMaximumHeight(100)
        self.address_input.setText(self.user_info.get('address', ''))
        self.address_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                color: black;
            }
        """)
        address_layout.addWidget(self.address_input)
        customer_layout.addWidget(address_widget)
        
        container_layout.addWidget(customer_group)
        
        # Order Summary
        summary_group = QGroupBox("Order Summary")
        summary_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                margin-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: black;
            }
        """)
        
        summary_layout = QVBoxLayout(summary_group)
        
        # Calculate totals
        subtotal = sum(Decimal(str(item['price'])) * Decimal(str(item['quantity'])) for item in self.cart_items)
        tax = subtotal * Decimal('0.12')
        total = subtotal + tax
        
        # Create summary table
        summary_table = QTableWidget()
        summary_table.setColumnCount(4)
        summary_table.setHorizontalHeaderLabels(["Item", "Price", "Qty", "Total"])
        summary_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        summary_table.setRowCount(len(self.cart_items))
        
        for row, item in enumerate(self.cart_items):
            summary_table.setItem(row, 0, QTableWidgetItem(item['item_name']))
            summary_table.setItem(row, 1, QTableWidgetItem(f"₱{float(item['price']):.2f}"))
            summary_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            item_total = Decimal(str(item['price'])) * Decimal(str(item['quantity']))
            summary_table.setItem(row, 3, QTableWidgetItem(f"₱{float(item_total):.2f}"))
        
        summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        summary_table.setMaximumHeight(200)
        summary_layout.addWidget(summary_table)
        
        # Totals
        totals_widget = QWidget()
        totals_layout = QVBoxLayout(totals_widget)
        
        # Subtotal
        subtotal_widget = QWidget()
        subtotal_row = QHBoxLayout(subtotal_widget)
        subtotal_row.addWidget(QLabel("Subtotal:"))
        subtotal_row.addStretch()
        subtotal_row.addWidget(QLabel(f"₱{float(subtotal):.2f}"))
        totals_layout.addWidget(subtotal_widget)
        
        # Tax
        tax_widget = QWidget()
        tax_row = QHBoxLayout(tax_widget)
        tax_row.addWidget(QLabel("Tax (12%):"))
        tax_row.addStretch()
        tax_row.addWidget(QLabel(f"₱{float(tax):.2f}"))
        totals_layout.addWidget(tax_widget)
        
        # Total
        total_widget = QWidget()
        total_row = QHBoxLayout(total_widget)
        total_label = QLabel("Total:")
        total_label.setStyleSheet("font-weight: bold;")
        total_row.addWidget(total_label)
        total_row.addStretch()
        total_value = QLabel(f"₱{float(total):.2f}")
        total_value.setStyleSheet("font-weight: bold; color: #e74c3c; font-size: 16px;")
        total_row.addWidget(total_value)
        totals_layout.addWidget(total_widget)
        
        summary_layout.addWidget(totals_widget)
        container_layout.addWidget(summary_group)
        
        # Payment & Delivery Options
        options_group = QGroupBox("Payment & Delivery Options")
        options_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                margin-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: black;
            }
        """)
        
        options_layout = QFormLayout(options_group)
        options_layout.setVerticalSpacing(10)
        
        # Payment Method
        payment_label = QLabel("Payment Method *:")
        payment_label.setStyleSheet("font-size: 14px; color: black;")
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Credit Card", "Debit Card", "Cash on Delivery", "GCash", "Bank Transfer"])
        self.payment_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                color: black;
            }
        """)
        options_layout.addRow(payment_label, self.payment_combo)
        
        # Delivery Method
        delivery_label = QLabel("Delivery Method *:")
        delivery_label.setStyleSheet("font-size: 14px; color: black;")
        self.delivery_combo = QComboBox()
        self.delivery_combo.addItems(["Standard Shipping (3-5 days)", "Express Shipping (1-2 days)", "Store Pickup"])
        self.delivery_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                color: black;
            }
        """)
        options_layout.addRow(delivery_label, self.delivery_combo)
        
        container_layout.addWidget(options_group)
        
        # Set scroll area widget
        scroll_area.setWidget(container_widget)
        main_layout.addWidget(scroll_area)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.process_order)
        button_box.rejected.connect(self.reject)
        
        button_box.setStyleSheet("""
            QDialogButtonBox {
                background-color: white;
            }
            QDialogButtonBox QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton[text="OK"] {
                background: #5ab9ea;
                color: white;
            }
            QDialogButtonBox QPushButton[text="OK"]:hover {
                background: #78d1ff;
            }
            QDialogButtonBox QPushButton[text="Cancel"] {
                background: #95a5a6;
                color: white;
            }
            QDialogButtonBox QPushButton[text="Cancel"]:hover {
                background: #7f8c8d;
            }
        """)
        
        main_layout.addWidget(button_box)
    
    def process_order(self):
        # Validate inputs
        if not self.address_input.toPlainText().strip():
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("Please enter your shipping address")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet("""
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
            msg.exec()
            return
        
        try:
            # Prepare order items
            order_items = []
            for item in self.cart_items:
                order_item = {
                    'price': item['price'],
                    'quantity': item['quantity']
                }
                if item['item_type'] == 'product':
                    order_item['product_id'] = item['product_id']
                else:
                    order_item['pet_id'] = item['pet_id']
                order_items.append(order_item)
            
            # Calculate totals
            subtotal = sum(Decimal(str(item['price'])) * Decimal(str(item['quantity'])) for item in self.cart_items)
            tax = subtotal * Decimal('0.12')
            total = subtotal + tax
            
            # Get user info for order
            user_info = self.user_info
            
            # Create order with all information
            self.order_id = self.order_model.create_order(
                customer_id=self.user_id,
                staff_id=self.user_id,  # Customer is also the staff for online orders
                items=order_items,
                total_amount=float(total),
                payment_method=self.payment_combo.currentText(),
                order_status='Pending',
                notes=f"Delivery: {self.delivery_combo.currentText()}\nAddress: {self.address_input.toPlainText()}"
            )
            
            if self.order_id:
                # Clear cart
                self.cart_model.clear_cart(self.user_id)
                
                # Show success message with receipt option
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Order Successful")
                msg_box.setText(f"Your order #{self.order_id} has been placed!\n\n"
                               f"Total: ₱{float(total):.2f}\n"
                               f"Payment: {self.payment_combo.currentText()}\n"
                               f"Delivery: {self.delivery_combo.currentText()}\n\n"
                               "Would you like to print a receipt?")
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
                
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
                    self.print_receipt()
                
                self.accept()
            else:
                raise Exception("Failed to create order")
                
        except Exception as e:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Failed to process order: {str(e)}")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setStyleSheet("""
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
            msg.exec()
    
    def print_receipt(self):
        try:
            # Calculate totals
            subtotal = sum(Decimal(str(item['price'])) * Decimal(str(item['quantity'])) for item in self.cart_items)
            tax = subtotal * Decimal('0.12')
            total = subtotal + tax
            
            # Get current date and time
            current_datetime = QDateTime.currentDateTime()
            
            # Create receipt HTML
            receipt_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        margin: 20px;
                        font-size: 100px;
                        color: #000000;
                        line-height: 1.4;
                    }}
                    .receipt-container {{
                        width: 100%;
                        max-width: 500px;
                        margin: 0 auto;
                        border: 1px solid #000;
                        padding: 15px;
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 15px;
                        font-size: 100px;
                    }}
                    .store-name {{
                        font-size: 16px;
                        font-weight: bold;
                        margin: 5px 0;
                        font-size: 100px;
                    }}
                    .receipt-title {{
                        font-size: 14px;
                        margin: 5px 0;
                        font-size: 100px;
                    }}
                    .order-info {{
                        text-align: right;
                        margin: 10px 0;
                    }}
                    .divider {{
                        border-top: 1px solid #000;
                        margin: 10px 0;
                        font-size: 100px;
                    }}
                    .double-divider {{
                        border-top: 2px dashed #000;
                        margin: 10px 0;
                        font-size: 100px;
                    }}
                    .customer-info {{
                        margin: 10px 0;
                    }}
                    .info-row {{
                        margin: 3px 0;
                    }}
                    .items-table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }}
                    .items-table th {{
                        text-align: left;
                        padding: 15px 0;
                        border-bottom: 1px solid #000;
                        font-weight: bold;
                    }}
                    .items-table td {{
                        padding: 4px 0;
                        border-bottom: 1px dotted #ccc;
                    }}
                    .price-col {{
                        text-align: right;
                        width: 100px;
                    }}
                    .qty-col {{
                        text-align: center;
                        width: 100px;
                    }}
                    .total-col {{
                        text-align: right;
                        width: 100px;
                    }}
                    .totals {{
                        text-align: right;
                        margin-top: 10px;
                    }}
                    .total-row {{
                        margin: 3px 0;
                    }}
                    .grand-total {{
                        font-weight: bold;
                        font-size: 100px;
                        margin-top: 8px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 20px;
                        font-size: 100px;
                    }}
                    .contact-info {{
                        margin: 5px 0;
                        font-size: 100px;
                    }}
                </style>
            </head>
            <body>
                <div class="receipt-container">
                    <div class="header">
                        <div class="store-name">***********************</div>
                        <div class="store-name">CUDDLE CORNER</div>
                        <div class="receipt-title">Pet Shop Receipt</div>
                    </div>
        
                    <div class="order-info">
                        <div>Order #: {self.order_id}</div>
                        <div>{current_datetime.toString('MMMM d, yyyy')}</div>
                    </div>
        
                    <div class="double-divider"></div>
        
                    <div class="customer-info">
                        <div class="info-row"><strong>Customer:</strong> {self.user_info.get('first_name', '')} {self.user_info.get('last_name', '')}</div>
                        <div class="info-row"><strong>Email:</strong> {self.user_info.get('email', '')}</div>
                        <div class="info-row"><strong>Shipping Address:</strong> {self.address_input.toPlainText()}</div>
                        <div class="info-row"><strong>Payment Method:</strong> {self.payment_combo.currentText()}</div>
                        <div class="info-row"><strong>Delivery Method:</strong> {self.delivery_combo.currentText()}</div>
                    </div>
        
                    <div class="divider"></div>
        
                    <table class="items-table">
                        <thead>
                            <tr>
                                <th>ITEM</th>
                                <th class="price-col">PRICE</th>
                                <th class="qty-col">QTY</th>
                                <th class="total-col">TOTAL</th>
                            </tr>
                        </thead>
                        <tbody>
            """

            # Add cart items
            for item in self.cart_items:
                item_total = Decimal(str(item['price'])) * Decimal(str(item['quantity']))
                receipt_html += f"""
                            <tr>
                                <td>{item['item_name']}</td>
                                <td class="price-col">₱{float(item['price']):.2f}</td>
                                <td class="qty-col">{item['quantity']}</td>
                                <td class="total-col">₱{float(item_total):.2f}</td>
                            </tr>
                """

            receipt_html += f"""
                        </tbody>
                    </table>
        
                    <div class="divider"></div>
        
                    <div class="totals">
                        <div class="total-row">Subtotal: ₱{float(subtotal):.2f}</div>
                        <div class="total-row">Tax (12%): ₱{float(tax):.2f}</div>
                        <div class="total-row grand-total">Total: ₱{float(total):.2f}</div>
                    </div>
        
                    <div class="double-divider"></div>
        
                    <div class="footer">
                        <div>Thank you for your purchase!</div>
                        <div class="contact-info">For inquiries, contact: CuddleCorner@test.com | 1234-567-890</div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create printer dialog 
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            
            # CORRECT: Using QPageLayout.Orientation.Portrait as shown in error message
            printer.setPageOrientation(QPageLayout.Orientation.Portrait)
            
            print_dialog = QPrintDialog(printer, self)
            if print_dialog.exec() == QDialog.DialogCode.Accepted:
                # Create document and print
                document = QTextDocument()
                document.setHtml(receipt_html)
                document.print(printer)
                
                # Also save as PDF
                save_path = f"receipt_order_{self.order_id}.pdf"
                printer.setOutputFileName(save_path)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                document.print(printer)
                
                msg = QMessageBox(self)
                msg.setWindowTitle("Success")
                msg.setText(f"Receipt printed successfully!\n\nSaved as: {save_path}")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setStyleSheet("""
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
                msg.exec()
                
        except Exception as e:
            msg = QMessageBox(self)
            msg.setWindowTitle("Print Error")
            msg.setText(f"Failed to print receipt: {str(e)}")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet("""
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
            msg.exec()
