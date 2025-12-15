from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QComboBox, QSpinBox, QMessageBox,
                             QHeaderView, QGroupBox, QDialog, QFormLayout,
                             QDialogButtonBox, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt
from models.product_model import ProductModel
from models.pet_model import PetModel
from models.order_model import OrderModel
from models.user_model import UserModel

class POSPanel(QWidget):
    def __init__(self, db, user_id, user_role):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.user_role = user_role
        self.product_model = ProductModel(db)
        self.pet_model = PetModel(db)
        self.order_model = OrderModel(db)
        self.user_model = UserModel(db)
        self.current_cart = []
        self.products = []
        self.pets = []
        self.init_ui()
        self.load_products()
        self.load_pets()
    
    def init_ui(self):
        self.setStyleSheet("""
            background-color: white;
            color: black;
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Left side - Products and Pets
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setSpacing(15)
        
        # Header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        title = QLabel("POS System")
        title.setStyleSheet("""
            background-color: white;
            font-size: 25px; 
            font-weight: bold; 
            color: black;
            padding: 10px 0;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        left_layout.addWidget(header_widget)
        left_layout.addSpacing(10)
        
        # Search and filter
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)

        # Category filter
        category_label = QLabel("Category:")
        category_label.setStyleSheet("""
            QLabel {    
                background-color: white;
                color: black;
                padding: 5px 10px;
            }
        """)
        filter_layout.addWidget(category_label)

        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("""
            QComboBox {
                color: black;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                border: 1px solid #ddd;
            }
        """)
        self.category_combo.addItems(["All Items", "Products", "Pets"])
        self.category_combo.currentTextChanged.connect(self.filter_items)
        filter_layout.addWidget(self.category_combo)
        
        # Search
        search_label = QLabel("Search:")
        search_label.setStyleSheet("""
            QLabel {    
                background-color: white;
                color: black;
                padding: 5px 10px;
                margin-left: 20px;
            }
        """)
        filter_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, category...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                color: black;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        self.search_input.textChanged.connect(self.search_items)
        filter_layout.addWidget(self.search_input)

        filter_layout.addStretch()
        left_layout.addWidget(filter_widget)
        left_layout.addSpacing(20)
        
        # Items grid with scroll area
        self.items_scroll = QScrollArea()
        self.items_scroll.setWidgetResizable(True)
        self.items_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e1e1e1;
                border-radius: 8px;
                background: white;
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
        
        # Create container widget for scroll area
        scroll_widget = QWidget()
        self.items_layout = QVBoxLayout(scroll_widget)
        self.items_layout.setSpacing(10)
        self.items_scroll.setWidget(scroll_widget)
        
        left_layout.addWidget(self.items_scroll)
        
        # Right side - Cart and checkout
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
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
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: black;
            }
        """)
        
        cart_group_layout = QVBoxLayout(cart_group)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Price", "Qty", "Total", "Actions"])
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
        cart_group_layout.addWidget(self.cart_table)
        
        # Cart totals
        totals_widget = QWidget()
        totals_layout = QVBoxLayout(totals_widget)
        totals_layout.setSpacing(5)
        
        # Subtotal row
        subtotal_widget = QWidget()
        subtotal_layout = QHBoxLayout(subtotal_widget)
        subtotal_label = QLabel("Subtotal:")
        subtotal_label.setStyleSheet("color: black;")
        subtotal_layout.addWidget(subtotal_label)
        self.subtotal_label = QLabel("₱0.00")
        self.subtotal_label.setStyleSheet("font-weight: bold; color: black;")
        subtotal_layout.addStretch()
        subtotal_layout.addWidget(self.subtotal_label)
        totals_layout.addWidget(subtotal_widget)
        
        # Tax row
        tax_widget = QWidget()
        tax_layout = QHBoxLayout(tax_widget)
        tax_label = QLabel("Tax (12%):")
        tax_label.setStyleSheet("color: black;")
        tax_layout.addWidget(tax_label)
        self.tax_label = QLabel("₱0.00")
        self.tax_label.setStyleSheet("font-weight: bold; color: black;")
        tax_layout.addStretch()
        tax_layout.addWidget(self.tax_label)
        totals_layout.addWidget(tax_widget)
        
        # Total row
        total_widget = QWidget()
        total_layout = QHBoxLayout(total_widget)
        total_label = QLabel("Total:")
        total_label.setStyleSheet("color: black;")
        total_layout.addWidget(total_label)
        self.total_label = QLabel("₱0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c;")
        total_layout.addStretch()
        total_layout.addWidget(self.total_label)
        totals_layout.addWidget(total_widget)
        
        cart_group_layout.addWidget(totals_widget)
        cart_group_layout.addSpacing(10)
        
        # Customer Info Section
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
        
        customer_group_layout = QVBoxLayout(customer_group)
        
        # Customer name input
        name_widget = QWidget()
        customer_name_layout = QHBoxLayout(name_widget)
        customer_name_label = QLabel("Customer Name:")
        customer_name_label.setStyleSheet("color: black;")
        customer_name_layout.addWidget(customer_name_label)
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Enter customer name")
        self.customer_name_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                color: black;
            }
        """)
        customer_name_layout.addWidget(self.customer_name_input)
        customer_group_layout.addWidget(name_widget)
        
        # Customer search/combo box
        customer_select_widget = QWidget()
        existing_customer_layout = QHBoxLayout(customer_select_widget)
        existing_customer_label = QLabel("Select Customer:")
        existing_customer_label.setStyleSheet("color: black;")
        existing_customer_layout.addWidget(existing_customer_label)
        self.customer_combo = QComboBox()
        self.customer_combo.addItem("New Customer")
        self.load_existing_customers()
        self.customer_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                color: black;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
            }
        """)
        self.customer_combo.currentTextChanged.connect(self.on_customer_selected)
        existing_customer_layout.addWidget(self.customer_combo)
        customer_group_layout.addWidget(customer_select_widget)
        
        cart_group_layout.addWidget(customer_group)
        cart_group_layout.addSpacing(10)
        
        # Checkout buttons
        checkout_widget = QWidget()
        checkout_layout = QHBoxLayout(checkout_widget)
        
        clear_btn = QPushButton("Clear Cart")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        clear_btn.clicked.connect(self.clear_cart)
        
        checkout_btn = QPushButton("Proceed to Checkout")
        checkout_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        checkout_btn.clicked.connect(self.checkout)
        
        checkout_layout.addWidget(clear_btn)
        checkout_layout.addWidget(checkout_btn)
        cart_group_layout.addWidget(checkout_widget)
        
        right_layout.addWidget(cart_group)
        
        # Add left and right containers to main layout
        main_layout.addWidget(left_container, 2)
        main_layout.addWidget(right_container, 1)
    
    def load_existing_customers(self):
        """Load existing customers from users table"""
        users = self.user_model.get_all_users()
        for user in users:
            if user.get('role') == 'customer' or user.get('role') != 'admin':
                full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                if full_name:
                    self.customer_combo.addItem(f"{full_name} (ID: {user['id']})")
                elif user.get('username'):
                    self.customer_combo.addItem(f"{user['username']} (ID: {user['id']})")
    
    def get_or_create_customer(self, customer_name):
        """Get existing customer ID or create new customer in users table"""
        try:
            customer = self.user_model.get_user_by_username(customer_name)
            
            if not customer:
                users = self.user_model.get_all_users()
                for user in users:
                    full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                    if full_name.lower() == customer_name.lower():
                        return user['id']
            
                user_data = {
                    'username': customer_name.lower().replace(' ', '_'),
                    'password': 'customer123',
                    'email': f"{customer_name.lower().replace(' ', '.')}@example.com",
                    'first_name': customer_name.split()[0] if ' ' in customer_name else customer_name,
                    'last_name': customer_name.split()[1] if ' ' in customer_name else '',
                    'phone': '',
                    'address': '',
                    'role': 'customer',
                    'is_active': 1
                }
                
                customer_id = self.user_model.create_user(user_data)
                return customer_id
            
            return customer['id']
            
        except Exception as e:
            print(f"Error in get_or_create_customer: {e}")
            return None
    
    def on_customer_selected(self, customer_text):
        """When customer is selected from dropdown"""
        if customer_text != "New Customer":
            customer_name = customer_text.split(' (ID:')[0].strip()
            self.customer_name_input.setText(customer_name)
    
    def load_products(self):
        self.products = self.product_model.get_all_products()
        self.display_items()
    
    def load_pets(self):
        self.pets = self.pet_model.get_all_pets('Available')
        self.display_items()

    def search_items(self, text):
        """Search items by name"""
        text = text.lower()
        
        # Iterate through all group boxes
        for i in range(self.items_layout.count()):
            group_box = self.items_layout.itemAt(i).widget()
            if group_box:
                # Get the main layout of the group box
                group_layout = group_box.layout()
                if group_layout:
                    # Get the grid layout inside the group box
                    grid_layout = None
                    for j in range(group_layout.count()):
                        item = group_layout.itemAt(j)
                        if item and item.layout():
                            grid_layout = item.layout()
                            break
                    
                    if grid_layout:
                        # Search through grid items
                        for j in range(grid_layout.count()):
                            item_widget = grid_layout.itemAt(j).widget()
                            if item_widget:
                                # Find QLabel children to search in their text
                                found = False
                                for child in item_widget.findChildren(QLabel):
                                    if child and child.text():
                                        if text in child.text().lower():
                                            found = True
                                            break
                                
                                if found:
                                    item_widget.show()
                                else:
                                    item_widget.hide()

    def filter_items(self, category):
        # Filter items by category
        for i in range(self.items_layout.count()):
            group_box = self.items_layout.itemAt(i).widget()
            if group_box:
                group_name = group_box.title().lower()
                
                if category == "All Items":
                    group_box.show()
                elif category == "Products":
                    if "products" in group_name:
                        group_box.show()
                    else:
                        group_box.hide()
                elif category == "Pets":
                    if "pets" in group_name:
                        group_box.show()
                    else:
                        group_box.hide()
    
    def display_items(self):
        # Display all items in the grid
        # Clear existing items
        for i in reversed(range(self.items_layout.count())): 
            widget = self.items_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Display products in grid layout
        products_group = QGroupBox("Products")
        products_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e1e1e1;
                border-radius: 8px;
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
        
        products_main_layout = QVBoxLayout(products_group)
        products_grid = QGridLayout()
        products_grid.setHorizontalSpacing(10)
        products_grid.setVerticalSpacing(10)
        products_grid.setContentsMargins(10, 10, 10, 10)
        
        row = 0
        col = 0
        for product in self.products:
            if product['quantity'] > 0:
                item_widget = self.create_product_item(product)
                if item_widget:
                    products_grid.addWidget(item_widget, row, col)
                    col += 1
                    if col == 3:
                        col = 0
                        row += 1
        
        products_main_layout.addLayout(products_grid)
        self.items_layout.addWidget(products_group)
        
        # Display pets in grid layout
        pets_group = QGroupBox("Available Pets")
        pets_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e1e1e1;
                border-radius: 8px;
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
        
        pets_main_layout = QVBoxLayout(pets_group)
        pets_grid = QGridLayout()
        pets_grid.setHorizontalSpacing(10)
        pets_grid.setVerticalSpacing(10)
        pets_grid.setContentsMargins(10, 10, 10, 10)
        
        row = 0
        col = 0
        for pet in self.pets:
            item_widget = self.create_pet_item(pet)
            if item_widget:
                pets_grid.addWidget(item_widget, row, col)
                col += 1
                if col == 3:
                    col = 0
                    row += 1
        
        pets_main_layout.addLayout(pets_grid)
        self.items_layout.addWidget(pets_group)
    
    def create_product_item(self, product):
        # Create a widget for a product item
        widget = QWidget()
        widget.setFixedWidth(200)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(3)
        
        # Product info
        name_label = QLabel(product['name'])
        name_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 13px; 
            color: black;
            qproperty-wordWrap: true;
        """)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setObjectName("item_name")  # Add object name for searching
        
        price_label = QLabel(f"₱{product['price']:.2f}")
        price_label.setStyleSheet("""
            color: #27ae60; 
            font-weight: bold; 
            font-size: 12px;
        """)
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        stock_label = QLabel(f"Stock: {product['quantity']}")
        stock_label.setStyleSheet("""
            color: black; 
            font-size: 10px;
        """)
        stock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add to cart section
        cart_widget = QWidget()
        cart_layout = QHBoxLayout(cart_widget)
        cart_layout.setSpacing(3)
        cart_layout.setContentsMargins(0, 0, 0, 0)
        
        qty_label = QLabel("Qty:")
        qty_label.setStyleSheet("""
            color: black; 
            font-size: 10px;
        """)
        qty_label.setMaximumHeight(20)
        
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, min(10, product['quantity']))
        quantity_spin.setValue(1)
        quantity_spin.setStyleSheet("""
            QSpinBox {
                padding: 2px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
                color: black;
                max-height: 20px;
            }
        """)
        quantity_spin.setMaximumHeight(20)
        
        add_btn = QPushButton("Add")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                padding: 3px 8px;
                border: none;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
                max-height: 20px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        add_btn.setMaximumHeight(20)
        add_btn.clicked.connect(lambda: self.add_product_to_cart(product, quantity_spin.value()))
        
        cart_layout.addWidget(qty_label)
        cart_layout.addWidget(quantity_spin)
        cart_layout.addWidget(add_btn)
        
        layout.addWidget(name_label)
        layout.addWidget(price_label)
        layout.addWidget(stock_label)
        layout.addWidget(cart_widget)
        
        widget.setStyleSheet("""
            QWidget {
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                background-color: white;
            }
            QWidget:hover {
                background: #f8f9fa;
            }
        """)
        
        return widget
    
    def create_pet_item(self, pet):
        # Create a widget for a pet item
        widget = QWidget()
        widget.setFixedWidth(200)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(3)
        
        # Pet info
        name_label = QLabel(pet['name'])
        name_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 13px; 
            color: black;
            qproperty-wordWrap: true;
        """)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setObjectName("item_name")  # Add object name for searching
        
        breed_label = QLabel(f"{pet['species']} - {pet['breed']}")
        breed_label.setStyleSheet("""
            color: black; 
            font-size: 10px;
        """)
        breed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        price_label = QLabel(f"₱{pet['price']:.2f}")
        price_label.setStyleSheet("""
            color: #e74c3c; 
            font-weight: bold; 
            font-size: 12px;
        """)
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add to cart button
        add_btn = QPushButton("Add to Cart")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                padding: 4px 10px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
                font-size: 11px;
                max-height: 20px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        add_btn.setMaximumHeight(20)
        add_btn.clicked.connect(lambda: self.add_pet_to_cart(pet))
        
        layout.addWidget(name_label)
        layout.addWidget(breed_label)
        layout.addWidget(price_label)
        layout.addWidget(add_btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        widget.setStyleSheet("""
            QWidget {
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                background-color: white;
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
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"₱{item['price']:.2f}"))
            
            # Quantity with spin box for products
            if item['type'] == 'product':
                quantity_widget = QWidget()
                quantity_layout = QHBoxLayout(quantity_widget)
                quantity_layout.setContentsMargins(0, 0, 0, 0)
                
                quantity_spin = QSpinBox()
                quantity_spin.setRange(1, item['max_quantity'])
                quantity_spin.setValue(item['quantity'])
                quantity_spin.valueChanged.connect(lambda value, r=row: self.update_cart_quantity(r, value))
                quantity_spin.setStyleSheet("""
                    QSpinBox {
                        padding: 2px;
                        border: 1px solid #ddd;
                        border-radius: 3px;
                        background-color: white;
                        color: black;
                        max-height: 20px;
                    }
                """)
                quantity_spin.setMaximumHeight(20)
                
                quantity_layout.addWidget(quantity_spin)
                self.cart_table.setCellWidget(row, 2, quantity_widget)
            else:
                self.cart_table.setItem(row, 2, QTableWidgetItem("1"))
            
            item_total = item['price'] * item['quantity']
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"₱{item_total:.2f}"))
            subtotal += item_total
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background: #dc3545;
                    color: white;
                    padding: 3px 8px;
                    border: none;
                    border-radius: 3px;
                    font-size: 11px;
                    font-weight: bold;
                    max-height: 20px;
                }
                QPushButton:hover {
                    background: #c82333;
                }
            """)
            remove_btn.setMaximumHeight(20)
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 4, remove_btn)
        
        # Update totals with 12% tax
        tax = subtotal * 0.12
        total = subtotal + tax
        
        self.subtotal_label.setText(f"₱{subtotal:.2f}")
        self.tax_label.setText(f"₱{tax:.2f}")
        self.total_label.setText(f"₱{total:.2f}")
    
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
        
        # Get customer name
        customer_name = self.customer_name_input.text().strip()
        if not customer_name:
            QMessageBox.warning(self, "Customer Name Required", 
                              "Please enter customer name or select existing customer")
            return
        
        # Show checkout dialog with customer name
        dialog = CheckoutDialog(self.current_cart, self.user_id, self.order_model, 
                               self.user_model, customer_name)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_cart.clear()
            self.customer_name_input.clear()
            self.update_cart_display()
            self.load_products()
            self.load_pets()
            self.load_existing_customers()


class CheckoutDialog(QDialog):
    def __init__(self, cart_items, user_id, order_model, user_model, customer_name):
        super().__init__()
        self.cart_items = cart_items
        self.user_id = user_id
        self.order_model = order_model
        self.user_model = user_model
        self.customer_name = customer_name
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Checkout")
        self.setModal(True)
        self.resize(500, 500)
        self.setStyleSheet("""
            background-color: white;
            color: black;
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
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
        customer_name_label = QLabel(f"Customer: {self.customer_name}")
        customer_name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: black;")
        customer_layout.addWidget(customer_name_label)
        
        layout.addWidget(customer_group)
        
        # Order summary
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
        
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(4)
        self.summary_table.setHorizontalHeaderLabels(["Item", "Price", "Qty", "Total"])
        self.summary_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.summary_table.setStyleSheet("""
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
        
        subtotal = 0
        self.summary_table.setRowCount(len(self.cart_items))
        for row, item in enumerate(self.cart_items):
            self.summary_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.summary_table.setItem(row, 1, QTableWidgetItem(f"₱{item['price']:.2f}"))
            self.summary_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            item_total = item['price'] * item['quantity']
            self.summary_table.setItem(row, 3, QTableWidgetItem(f"₱{item_total:.2f}"))
            subtotal += item_total
        
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        summary_layout.addWidget(self.summary_table)
        
        # Totals with 12% tax
        tax = subtotal * 0.12
        total = subtotal + tax
        
        # Create totals widget
        totals_widget = QWidget()
        totals_layout = QVBoxLayout(totals_widget)
        totals_layout.setSpacing(5)
        
        # Subtotal row
        subtotal_widget = QWidget()
        subtotal_row_layout = QHBoxLayout(subtotal_widget)
        subtotal_label = QLabel("Subtotal:")
        subtotal_label.setStyleSheet("color: black;")
        subtotal_row_layout.addWidget(subtotal_label)
        subtotal_row_layout.addStretch()
        subtotal_value = QLabel(f"₱{subtotal:.2f}")
        subtotal_value.setStyleSheet("color: black;")
        subtotal_row_layout.addWidget(subtotal_value)
        totals_layout.addWidget(subtotal_widget)
        
        # Tax row
        tax_widget = QWidget()
        tax_row_layout = QHBoxLayout(tax_widget)
        tax_label = QLabel("Tax (12%):")
        tax_label.setStyleSheet("color: black;")
        tax_row_layout.addWidget(tax_label)
        tax_row_layout.addStretch()
        tax_value = QLabel(f"₱{tax:.2f}")
        tax_value.setStyleSheet("color: black;")
        tax_row_layout.addWidget(tax_value)
        totals_layout.addWidget(tax_widget)
        
        # Total row
        total_widget = QWidget()
        total_row_layout = QHBoxLayout(total_widget)
        total_label = QLabel("Total:")
        total_label.setStyleSheet("color: black;")
        total_row_layout.addWidget(total_label)
        total_row_layout.addStretch()
        total_value = QLabel(f"₱{total:.2f}")
        total_value.setStyleSheet("font-weight: bold; color: #e74c3c; font-size: 16px;")
        total_row_layout.addWidget(total_value)
        totals_layout.addWidget(total_widget)
        
        summary_layout.addWidget(totals_widget)
        layout.addWidget(summary_group)
        
        # Payment method
        payment_group = QGroupBox("Payment Method")
        payment_group.setStyleSheet("""
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
        
        payment_layout = QFormLayout(payment_group)
        
        payment_label = QLabel("Payment Method:")
        payment_label.setStyleSheet("color: black;")
        
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash", "Credit Card", "Debit Card", "Mobile Payment"])
        self.payment_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                color: black;
            }
        """)
        payment_layout.addRow(payment_label, self.payment_combo)
        
        layout.addWidget(payment_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.process_payment)
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
                background: #3498db;
                color: white;
            }
            QDialogButtonBox QPushButton[text="OK"]:hover {
                background: #2980b9;
            }
            QDialogButtonBox QPushButton[text="Cancel"] {
                background: #95a5a6;
                color: white;
            }
            QDialogButtonBox QPushButton[text="Cancel"]:hover {
                background: #7f8c8d;
            }
        """)
        
        layout.addWidget(button_box)
    
    def process_payment(self):
        try:
            # Get or create customer for checkout
            customer_id = self.get_or_create_customer_for_checkout()
            
            if not customer_id:
                QMessageBox.warning(self, "Error", "Failed to process customer information")
                return
            
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
            
            # Calculate total with 12% tax
            subtotal = sum(item['price'] * item['quantity'] for item in self.cart_items)
            total = subtotal * 1.12
            
            # Create order
            order_id = self.order_model.create_order(
                customer_id=customer_id,
                staff_id=self.user_id,
                items=order_items,
                total_amount=total,
                payment_method=self.payment_combo.currentText(),
                order_status='Completed',
                notes=f"POS order for {self.customer_name}"
            )
            
            if order_id:
                QMessageBox.information(self, "Success", 
                                      f"Order #{order_id} completed successfully!\n"
                                      f"Customer: {self.customer_name}\n"
                                      f"Total: ₱{total:.2f}")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to process order")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def get_or_create_customer_for_checkout(self):
        # Helper method to get or create customer for checkout
        try:
            customer = self.user_model.get_user_by_username(self.customer_name.lower().replace(' ', '_'))
            
            if not customer:
                users = self.user_model.get_all_users()
                for user in users:
                    full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                    if full_name.lower() == self.customer_name.lower():
                        return user['id']
                
                user_data = {
                    'username': self.customer_name.lower().replace(' ', '_'),
                    'password': 'customer123',
                    'email': f"{self.customer_name.lower().replace(' ', '.')}@example.com",
                    'first_name': self.customer_name.split()[0] if ' ' in self.customer_name else self.customer_name,
                    'last_name': self.customer_name.split()[1] if ' ' in self.customer_name else '',
                    'phone': '',
                    'address': '',
                    'role': 'customer',
                    'is_active': 1
                }
                
                customer_id = self.user_model.create_user(user_data)
                return customer_id
            
            return customer['id']
            
        except Exception as e:
            print(f"Error creating customer: {e}")
            return None
