from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QGroupBox, QSpinBox)
from PyQt6.QtCore import Qt
from decimal import Decimal
from models.cart_model import CartModel
from models.order_model import OrderModel

class CartPanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.cart_model = CartModel(db)
        self.order_model = OrderModel(db)
        self.init_ui()
        self.load_cart()
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("My Shopping Cart")
        title.setStyleSheet("background-color: #f9fafb; font-size: 40px; font-weight: bold; color: black;")
        layout.addWidget(title)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Type", "Price", "Quantity", "Total", "Actions"])
        
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
        
        summary_group = QGroupBox("Order Summary")
        summary_group.setStyleSheet("color: black;")
        summary_layout = QVBoxLayout()
        
        totals_layout = QVBoxLayout()
        
        subtotal_layout = QHBoxLayout()
        subtotal_layout.addWidget(QLabel("Subtotal:"))
        self.subtotal_label = QLabel("₱0.00")
        self.subtotal_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        subtotal_layout.addStretch()
        subtotal_layout.addWidget(self.subtotal_label)
        
        tax_layout = QHBoxLayout()
        tax_layout.addWidget(QLabel("Tax (12%):"))
        self.tax_label = QLabel("₱0.00")
        self.tax_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        tax_layout.addStretch()
        tax_layout.addWidget(self.tax_label)
        
        total_layout = QHBoxLayout()
        total_text_label = QLabel("Total:")
        total_text_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        total_layout.addWidget(total_text_label)
        
        self.total_label = QLabel("₱0.00")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e74c3c;")
        total_layout.addStretch()
        total_layout.addWidget(self.total_label)
        
        totals_layout.addLayout(subtotal_layout)
        totals_layout.addLayout(tax_layout)
        totals_layout.addLayout(total_layout)
        summary_layout.addLayout(totals_layout)
        
        checkout_btn = QPushButton("Proceed to Checkout")
        checkout_btn.setStyleSheet("""
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
                background: #5ab9ea;
            }
            QPushButton:disabled {
                background: #95a5a6;
            }
        """)
        checkout_btn.clicked.connect(self.checkout)
        summary_layout.addWidget(checkout_btn)
        
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
            
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(item['item_name'])))
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(item['item_type']).title()))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"₱{float(item['price']):.2f}"))
            
            quantity_widget = QWidget()
            quantity_layout = QHBoxLayout()
            quantity_layout.setContentsMargins(0, 0, 0, 0)
            
            quantity_spin = QSpinBox()
            quantity_spin.setRange(1, 10 if item['item_type'] == 'product' else 1)
            quantity_spin.setValue(int(item['quantity']))
            quantity_spin.valueChanged.connect(lambda value, item_id=item['id']: self.update_quantity(item_id, value))
            
            quantity_layout.addWidget(quantity_spin)
            quantity_widget.setLayout(quantity_layout)
            self.cart_table.setCellWidget(row, 3, quantity_widget)
            
            item_total = Decimal(str(item['price'])) * Decimal(str(item['quantity']))
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"₱{float(item_total):.2f}"))
            subtotal += item_total
            
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
        
        checkout_btn = self.findChild(QPushButton)
        if checkout_btn:
            checkout_btn.setEnabled(len(cart_items) > 0)
    
    def update_quantity(self, cart_id, quantity):
        if self.cart_model.update_cart_quantity(cart_id, quantity):
            self.load_cart()
        else:
            QMessageBox.warning(self, "Error", "Failed to update quantity")
    
    def remove_item(self, cart_id):
        reply = QMessageBox.question(self, "Remove Item", 
                                   "Are you sure you want to remove this item from your cart?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.cart_model.remove_from_cart(cart_id):
                QMessageBox.information(self, "Success", "Item removed from cart")
                self.load_cart()
            else:
                QMessageBox.warning(self, "Error", "Failed to remove item")
    
    def checkout(self):
        cart_items = self.cart_model.get_cart_items(self.user_id)
        if not cart_items:
            QMessageBox.warning(self, "Empty Cart", "Your cart is empty")
            return
        
        order_items = []
        for item in cart_items:
            order_item = {
                'price': item['price'],
                'quantity': item['quantity']
            }
            if item['item_type'] == 'product':
                order_item['product_id'] = item['product_id']
            else:
                order_item['pet_id'] = item['pet_id']
            order_items.append(order_item)
        
        subtotal = sum(item['price'] * Decimal(str(item['quantity'])) for item in cart_items)
        total = subtotal * Decimal('1.08')
        
        order_id = self.order_model.create_order(self.user_id, order_items, total, "Credit Card")
        
        if order_id:
            self.cart_model.clear_cart(self.user_id)
            QMessageBox.information(self, "Order Successful", 
                                  f"Your order #{order_id} has been placed!\n"
                                  f"Total: ₱{total:.2f}")
            self.load_cart()
        else:
            QMessageBox.warning(self, "Order Failed", "Failed to process your order")