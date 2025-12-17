from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QComboBox, QLineEdit,
                             QMessageBox, QGroupBox, QSpinBox, QGridLayout)
from PyQt6.QtCore import Qt
import os
from PyQt6.QtGui import QPixmap
from models.product_model import ProductModel
from models.cart_model import CartModel

class CustomerProductsPanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.product_model = ProductModel(db)
        self.cart_model = CartModel(db)
        self.all_products = []
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Available Products")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search and filter
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products by name, description, or category...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                min-width: 200px;
                color: black;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.textChanged.connect(self.search_products)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All Categories", "Food", "Accessories", "Medicine", "Toys", "Grooming"])
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: #f9fafb;
                padding: 8px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                min-width: 150px;
                color: black;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        self.category_combo.currentTextChanged.connect(self.filter_products)

        # Price filter
        self.price_combo = QComboBox()
        self.price_combo.addItems(["Any Price", "Under ₱50", "₱50 - ₱200", "₱200 - ₱500", "Over ₱500"])
        self.price_combo.setStyleSheet("""
            QComboBox {
                background-color: #f9fafb;
                padding: 8px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                min-width: 150px;
                color: black;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        self.price_combo.currentTextChanged.connect(self.filter_products)

        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        clear_btn.clicked.connect(self.clear_filters)
        
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.category_combo)
        header_layout.addWidget(self.price_combo)
        header_layout.addWidget(clear_btn)
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Products grid
        self.products_scroll = QScrollArea()
        self.products_widget = QWidget()
        self.products_layout = QHBoxLayout(self.products_widget)
        self.products_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.products_scroll.setWidget(self.products_widget)
        self.products_scroll.setWidgetResizable(True)
        
        layout.addWidget(self.products_scroll)
        self.setLayout(layout)
    
    def load_products(self):
        self.all_products = self.product_model.get_all_products()
        self.apply_filters()

    def apply_filters(self):
        filtered_products = self.all_products.copy()

        # Apply search filter
        search_text = self.search_input.text().strip().lower()
        if search_text:
            filtered_products = [product for product in filtered_products if
                                 search_text in product['name'].lower() or 
                                 search_text in product['category'].lower() or
                                 (product['description'] and search_text in product['description'].lower())]
        
        # Apply category filter
        category_filter = self.category_combo.currentText()
        if category_filter != "All Categories":
            filtered_products = [product for product in filtered_products if 
                               product['category'] == category_filter]
            
        # Apply price filter
        price_filter = self.price_combo.currentText()
        if price_filter == "Under ₱50":
            filtered_products = [product for product in filtered_products if product['price'] < 50]
        elif price_filter == "₱50 - ₱200":
            filtered_products = [product for product in filtered_products if 50 <= product['price'] <= 200]
        elif price_filter == "₱200 - ₱500":
            filtered_products = [product for product in filtered_products if 200 <= product['price'] <= 500]
        elif price_filter == "Over ₱500":
            filtered_products = [product for product in filtered_products if product['price'] > 500]

        self.display_products(filtered_products)

    def search_products(self):
        self.apply_filters()

    def filter_products(self):
        self.apply_filters()

    def clear_filters(self):
        self.search_input.clear()
        self.category_combo.setCurrentText("All Categories")
        self.price_combo.setCurrentText("Any Price")
        self.apply_filters()
    
    def display_products(self, products):
        # Clear existing products
        for i in reversed(range(self.products_layout.count())): 
            widget = self.products_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not products:
            no_results = QLabel("No products found matching your criteria.")
            no_results.setStyleSheet("color: black; font-size: 16px; text-align: center;")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_layout.addWidget(no_results)
            return
        
        # Create a grid layout for pets
        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Create container with QGridLayout
        container = QWidget()
        container_layout = QGridLayout(container)
        container_layout.setHorizontalSpacing(10)
        container_layout.setVerticalSpacing(20)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Calculate number of rows needed (4 items per row)
        num_rows = (len(products) + 1) // 4  # Integer division for rows
        
        # Add products to grid
        for i, products in enumerate(products):
            row = i // 4
            col = i % 4
            product_card = self.create_product_card(products)
            container_layout.addWidget(product_card, row, col)
                
        # Add container to grid widget
        grid_layout.addWidget(container)
        self.products_layout.addWidget(grid_widget)
    
    def create_product_card(self, product):
        card = QGroupBox()
        card.setFixedSize(300, 450)
        card.setStyleSheet("""
            QGroupBox {
                border: 2px solid #e1e1e1;
                border-radius: 10px;
                margin-top: 10px;
                padding: 15px;
                background: white;
            }
            QGroupBox:hover {
                border-color: #3498db;
                background: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Product image
        image_label = QLabel()
        image_label.setFixedSize(200, 200)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                border-radius: 5px;
                background: #f8f9fa;
            }
        """)
        
        if product['image_path'] and os.path.exists(product['image_path']):
            pixmap = QPixmap(product['image_path'])
            scaled_pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
        else:
            image_label.setText("No Image")
        
        layout.addWidget(image_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Product info
        name_label = QLabel(product['name'])
        name_label.setStyleSheet("background-color: white; font-weight: bold; font-size: 18px; color: black;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        category_label = QLabel(f"Category: {product['category']}")
        category_label.setStyleSheet("background-color: white; color: black; font-size: 14px;")
        layout.addWidget(category_label)

        # Details layout with aligned text
        details_layout = QHBoxLayout()
        details_layout.setSpacing(10)
        details_layout.setContentsMargins(0, 0, 0, 0)
        
        price_label = QLabel(f"₱{product['price']:.2f}")
        price_label.setStyleSheet("background-color: white; color: #e74c3c; font-size: 20px; font-weight: bold;")

        details_layout.addWidget(price_label)
        details_layout.addStretch()
        layout.addLayout(details_layout)
        
        if product['description']:
            desc_label = QLabel(product['description'])
            desc_label.setStyleSheet("background-color: white; color: black; font-size: 12px;")
            desc_label.setWordWrap(True)
            desc_label.setMaximumHeight(50)
            layout.addWidget(desc_label)
        
        # Add to cart section
        cart_layout = QHBoxLayout()
        cart_layout.setSpacing(10)
        qty_label = QLabel("Quantity:")
        qty_label.setStyleSheet("""
            QLabel {
                background-color: white;
                color: black;
                padding: 0px;
                margin: 0px;
            }
        """)
        cart_layout.addWidget(qty_label)
        
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, min(10, product['quantity']))
        quantity_spin.setValue(1)
        quantity_spin.setStyleSheet("""
            QSpinBox {
                padding: 4px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: black;
            }
        """)
        
        add_btn = QPushButton("Add to Cart")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #5ab9ea;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #78d1ff;
            }
            QPushButton:disabled {
                background: #95a5a6;
            }
        """)

        if product['quantity'] == 0:
            add_btn.setText("Out of Stock")
            add_btn.setDisabled(True)
            quantity_spin.setDisabled(True)
        else:
            add_btn.clicked.connect(lambda: self.add_to_cart(product['id'], quantity_spin.value()))
        
        cart_layout.addWidget(quantity_spin)
        cart_layout.addWidget(add_btn)
        layout.addLayout(cart_layout)
        
        card.setLayout(layout)
        return card
    
    def add_to_cart(self, product_id, quantity):
        try:
            result = self.cart_model.add_to_cart(self.user_id, 'product', product_id, quantity)
            if result:
            # Create styled message box
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Success")
                msg_box.setText("Product added to cart!")
                msg_box.setIcon(QMessageBox.Icon.Information)
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
                """)
                msg_box.exec()
            
                # Refresh the cart panel
                self.refresh_cart_panel()
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Error")
                msg_box.setText("Failed to add product to cart")
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setStyleSheet("""
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
                msg_box.exec()
        except Exception as e:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"An error occurred: {str(e)}")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStyleSheet("""
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
            msg_box.exec()
    
    def refresh_cart_panel(self):
        # CustomerDashboard has a direct reference to cart_panel
        parent = self.parent()
        while parent:
            if hasattr(parent, 'cart_panel'):
                parent.cart_panel.refresh_cart()
                return True
            parent = parent.parent()
        
        return False
