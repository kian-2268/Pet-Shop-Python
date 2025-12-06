from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QComboBox, QSpinBox, QMessageBox,
                             QHeaderView, QGroupBox, QDialog, QFormLayout,
                             QDialogButtonBox, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from models.product_model import ProductModel
from models.pet_model import PetModel
from models.order_model import OrderModel
from models.cart_model import CartModel

class POSPanel(QWidget):
    def __init__(self, db, user_id, username):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.user_role = username
        self.product_model = ProductModel(db)
        self.pet_model = PetModel(db)
        self.order_model = OrderModel(db)
        self.cart_model = CartModel(db)
        self.current_cart = []
        self.products = []
        self.pets = []
        self.init_ui()
        self.load_products()
        self.load_pets()
    
    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Left side - Products and Pets
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        
        # Search and filter
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products or pets...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        self.search_input.textChanged.connect(self.search_items)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All Items", "Products", "Pets"])
        self.category_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                min-width: 120px;
            }
        """)
        self.category_combo.currentTextChanged.connect(self.filter_items)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.category_combo)
        left_layout.addLayout(search_layout)
        
        # Items grid
        self.items_scroll = QScrollArea()
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_scroll.setWidget(self.items_widget)
        self.items_scroll.setWidgetResizable(True)
        self.items_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e1e1e1;
                border-radius: 8px;
                background: white;
            }
        """)
        left_layout.addWidget(self.items_scroll)
        
        # Right side - Cart and checkout
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        
        # Cart section
        cart_group = QGroupBox("Shopping Cart")
        cart_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        cart_layout = QVBoxLayout()
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Price", "Qty", "Total", "Actions"])
        self.cart_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e1e1e1;
                border-radius: 5px;
            }
        """)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        cart_layout.addWidget(self.cart_table)
        
        # Cart totals
        totals_layout = QVBoxLayout()
        
        subtotal_layout = QHBoxLayout()
        subtotal_layout.addWidget(QLabel("Subtotal:"))
        self.subtotal_label = QLabel("$0.00")
        self.subtotal_label.setStyleSheet("font-weight: bold;")
        subtotal_layout.addStretch()
        subtotal_layout.addWidget(self.subtotal_label)
        totals_layout.addLayout(subtotal_layout)
        
        tax_layout = QHBoxLayout()
        tax_layout.addWidget(QLabel("Tax (8%):"))
        self.tax_label = QLabel("$0.00")
        self.tax_label.setStyleSheet("font-weight: bold;")
        tax_layout.addStretch()
        tax_layout.addWidget(self.tax_label)
        totals_layout.addLayout(tax_layout)
        
        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel("Total:"))
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c;")
        total_layout.addStretch()
        total_layout.addWidget(self.total_label)
        totals_layout.addLayout(total_layout)
        
        cart_layout.addLayout(totals_layout)
        
        # Checkout buttons
        checkout_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear Cart")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        clear_btn.clicked.connect(self.clear_cart)
        
        checkout_btn = QPushButton("Checkout")
        checkout_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #219a52;
            }
        """)
        checkout_btn.clicked.connect(self.checkout)
        
        checkout_layout.addWidget(clear_btn)
        checkout_layout.addWidget(checkout_btn)
        cart_layout.addLayout(checkout_layout)
        
        cart_group.setLayout(cart_layout)
        right_layout.addWidget(cart_group)
        
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)
        self.setLayout(main_layout)
    
    def load_products(self):
        self.products = self.product_model.get_all_products()
        self.display_items()
    
    def load_pets(self):
        self.pets = self.pet_model.get_all_pets('Available')
        self.display_items()

    def search_items(self, text):
        text = text.lower()
    
        for i in range(self.items_layout.count()):
            group_box = self.items_layout.itemAt(i).widget()  # Products or Pets group
            layout = group_box.layout()
            for j in range(layout.count()):
                item_widget = layout.itemAt(j).widget()
                # Find the QLabel with the name (assumes first QLabel in info_layout is name)
                name_label = item_widget.findChild(QLabel)
                if name_label and text in name_label.text().lower():
                    item_widget.show()
                else:
                    item_widget.hide()

    def filter_items(self, category):
        for i in range(self.items_layout.count()):
            group_box = self.items_layout.itemAt(i).widget()
            layout = group_box.layout()
            group_name = group_box.title().lower()
        
            if category == "All Items":
                group_box.show()
                for j in range(layout.count()):
                    layout.itemAt(j).widget().show()
            elif category == "Products":
                if "products" in group_name:
                    group_box.show()
                    for j in range(layout.count()):
                        layout.itemAt(j).widget().show()
                else:
                    group_box.hide()
            elif category == "Pets":
                if "pets" in group_name:
                    group_box.show()
                    for j in range(layout.count()):
                        layout.itemAt(j).widget().show()
                else:
                    group_box.hide()
    
    def display_items(self):
        # Clear existing items
        for i in reversed(range(self.items_layout.count())): 
            self.items_layout.itemAt(i).widget().setParent(None)
        
        # Display products
        products_group = QGroupBox("Products")
        products_layout = QVBoxLayout()
        
        for product in self.products:
            if product['quantity'] > 0:  # Only show in-stock products
                item_widget = self.create_product_item(product)
                products_layout.addWidget(item_widget)
        
        products_group.setLayout(products_layout)
        self.items_layout.addWidget(products_group)
        
        # Display pets
        pets_group = QGroupBox("Available Pets")
        pets_layout = QVBoxLayout()
        
        for pet in self.pets:
            item_widget = self.create_pet_item(pet)
            pets_layout.addWidget(item_widget)
        
        pets_group.setLayout(pets_layout)
        self.items_layout.addWidget(pets_group)
    
    def create_product_item(self, product):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Product info
        info_layout = QVBoxLayout()
        name_label = QLabel(product['name'])
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        price_label = QLabel(f"${product['price']:.2f}")
        price_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        stock_label = QLabel(f"Stock: {product['quantity']}")
        stock_label.setStyleSheet("color: #666; font-size: 12px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(price_label)
        info_layout.addWidget(stock_label)
        
        # Add to cart section
        cart_layout = QHBoxLayout()
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, min(10, product['quantity']))
        quantity_spin.setValue(1)
        
        add_btn = QPushButton("Add to Cart")
        add_btn.setStyleSheet("""
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
        add_btn.clicked.connect(lambda: self.add_product_to_cart(product, quantity_spin.value()))
        
        cart_layout.addWidget(QLabel("Qty:"))
        cart_layout.addWidget(quantity_spin)
        cart_layout.addWidget(add_btn)
        
        info_layout.addLayout(cart_layout)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        widget.setLayout(layout)
        
        widget.setStyleSheet("""
            QWidget {
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                margin: 2px;
            }
            QWidget:hover {
                background: #f8f9fa;
            }
        """)
        
        return widget
    
    def create_pet_item(self, pet):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Pet info
        info_layout = QVBoxLayout()
        name_label = QLabel(pet['name'])
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        breed_label = QLabel(f"{pet['species']} - {pet['breed']}")
        breed_label.setStyleSheet("color: #666; font-size: 12px;")
        
        price_label = QLabel(f"${pet['price']:.2f}")
        price_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 16px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(breed_label)
        info_layout.addWidget(price_label)
        
        # Add to cart button
        add_btn = QPushButton("Add to Cart")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        add_btn.clicked.connect(lambda: self.add_pet_to_cart(pet))
        
        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(add_btn)
        widget.setLayout(layout)
        
        widget.setStyleSheet("""
            QWidget {
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                margin: 2px;
            }
            QWidget:hover {
                background: #f8f9fa;
            }
        """)
        
        return widget
    
    def add_product_to_cart(self, product, quantity):
        cart_item = {
            'type': 'product',
            'id': product['id'],
            'name': product['name'],
            'price': float(product['price']),
            'quantity': quantity,
            'max_quantity': product['quantity']
        }
        self.add_to_cart(cart_item)
    
    def add_pet_to_cart(self, pet):
        cart_item = {
            'type': 'pet',
            'id': pet['id'],
            'name': pet['name'],
            'price': float(pet['price']),
            'quantity': 1,
            'max_quantity': 1
        }
        self.add_to_cart(cart_item)
    
    def add_to_cart(self, item):
        # Check if item already in cart
        for i, cart_item in enumerate(self.current_cart):
            if cart_item['type'] == item['type'] and cart_item['id'] == item['id']:
                if cart_item['type'] == 'product':
                    new_quantity = cart_item['quantity'] + item['quantity']
                    if new_quantity <= cart_item['max_quantity']:
                        self.current_cart[i]['quantity'] = new_quantity
                    else:
                        QMessageBox.warning(self, "Stock Limit", 
                                          f"Cannot add more than {cart_item['max_quantity']} units")
                else:
                    QMessageBox.warning(self, "Already in Cart", "This pet is already in your cart")
                self.update_cart_display()
                return
        
        self.current_cart.append(item)
        self.update_cart_display()
        QMessageBox.information(self, "Added to Cart", f"{item['name']} added to cart")
    
    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.current_cart))
        
        subtotal = 0
        for row, item in enumerate(self.current_cart):
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"${item['price']:.2f}"))
            
            # Quantity with spin box for products
            if item['type'] == 'product':
                quantity_widget = QWidget()
                quantity_layout = QHBoxLayout()
                quantity_layout.setContentsMargins(0, 0, 0, 0)
                
                quantity_spin = QSpinBox()
                quantity_spin.setRange(1, item['max_quantity'])
                quantity_spin.setValue(item['quantity'])
                quantity_spin.valueChanged.connect(lambda value, r=row: self.update_cart_quantity(r, value))
                
                quantity_layout.addWidget(quantity_spin)
                quantity_widget.setLayout(quantity_layout)
                self.cart_table.setCellWidget(row, 2, quantity_widget)
            else:
                self.cart_table.setItem(row, 2, QTableWidgetItem("1"))
            
            item_total = item['price'] * item['quantity']
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"${item_total:.2f}"))
            subtotal += item_total
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background: #e74c3c;
                    color: white;
                    padding: 3px 8px;
                    border: none;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #c0392b;
                }
            """)
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 4, remove_btn)
        
        # Update totals
        tax = subtotal * 0.08
        total = subtotal + tax
        
        self.subtotal_label.setText(f"${subtotal:.2f}")
        self.tax_label.setText(f"${tax:.2f}")
        self.total_label.setText(f"${total:.2f}")
    
    def update_cart_quantity(self, row, quantity):
        if 0 <= row < len(self.current_cart):
            self.current_cart[row]['quantity'] = quantity
            self.update_cart_display()
    
    def remove_from_cart(self, row):
        if 0 <= row < len(self.current_cart):
            item_name = self.current_cart[row]['name']
            self.current_cart.pop(row)
            self.update_cart_display()
            QMessageBox.information(self, "Removed", f"{item_name} removed from cart")
    
    def clear_cart(self):
        if self.current_cart:
            reply = QMessageBox.question(self, "Clear Cart", 
                                       "Are you sure you want to clear the cart?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.current_cart.clear()
                self.update_cart_display()
    
    def checkout(self):
        if not self.current_cart:
            QMessageBox.warning(self, "Empty Cart", "Your cart is empty")
            return
        
        # Show checkout dialog
        dialog = CheckoutDialog(self.current_cart, self.user_id, self.order_model)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_cart.clear()
            self.update_cart_display()
            self.load_products()  # Refresh stock
            self.load_pets()      # Refresh available pets

class CheckoutDialog(QDialog):
    def __init__(self, cart_items, user_id, order_model):
        super().__init__()
        self.cart_items = cart_items
        self.user_id = user_id
        self.order_model = order_model
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Checkout")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Order summary
        summary_group = QGroupBox("Order Summary")
        summary_layout = QVBoxLayout()
        
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(4)
        self.summary_table.setHorizontalHeaderLabels(["Item", "Price", "Qty", "Total"])
        self.summary_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        subtotal = 0
        self.summary_table.setRowCount(len(self.cart_items))
        for row, item in enumerate(self.cart_items):
            self.summary_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.summary_table.setItem(row, 1, QTableWidgetItem(f"${item['price']:.2f}"))
            self.summary_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            item_total = item['price'] * item['quantity']
            self.summary_table.setItem(row, 3, QTableWidgetItem(f"${item_total:.2f}"))
            subtotal += item_total
        
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        summary_layout.addWidget(self.summary_table)
        
        # Totals
        tax = subtotal * 0.08
        total = subtotal + tax
        
        totals_layout = QVBoxLayout()
        
        subtotal_layout = QHBoxLayout()
        subtotal_layout.addWidget(QLabel("Subtotal:"))
        subtotal_layout.addStretch()
        subtotal_layout.addWidget(QLabel(f"${subtotal:.2f}"))
        
        tax_layout = QHBoxLayout()
        tax_layout.addWidget(QLabel("Tax (8%):"))
        tax_layout.addStretch()
        tax_layout.addWidget(QLabel(f"${tax:.2f}"))
        
        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel("Total:"))
        total_layout.addStretch()
        total_layout.addWidget(QLabel(f"${total:.2f}"))
        total_layout.itemAt(2).widget().setStyleSheet("font-weight: bold; color: #e74c3c; font-size: 16px;")
        
        totals_layout.addLayout(subtotal_layout)
        totals_layout.addLayout(tax_layout)
        totals_layout.addLayout(total_layout)
        summary_layout.addLayout(totals_layout)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Payment method
        payment_group = QGroupBox("Payment Method")
        payment_layout = QFormLayout()
        
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash", "Credit Card", "Debit Card", "Mobile Payment"])
        payment_layout.addRow("Payment Method:", self.payment_combo)
        
        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.process_payment)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def process_payment(self):
        try:
            # Prepare items for order
            order_items = []
            for item in self.cart_items:
                order_item = {
                    'price': item['price'],
                    'quantity': item['quantity']
                }
                if item['type'] == 'product':
                    order_item['product_id'] = item['id']
                else:
                    order_item['pet_id'] = item['id']
                order_items.append(order_item)
            
            # Calculate total
            subtotal = sum(item['price'] * item['quantity'] for item in self.cart_items)
            total = subtotal * 1.08  # Including tax
            
            # Create order
            order_id = self.order_model.create_order(
                self.user_id, 
                order_items, 
                total,
                self.payment_combo.currentText()
            )
            
            if order_id:
                QMessageBox.information(self, "Success", 
                                      f"Order #{order_id} completed successfully!\n"
                                      f"Total: ${total:.2f}")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to process order")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")