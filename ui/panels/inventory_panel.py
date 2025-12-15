from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QComboBox, QTextEdit, QDoubleSpinBox,
                             QSpinBox, QFileDialog, QMessageBox, QHeaderView,
                             QDialog, QDialogButtonBox, QGroupBox, QScrollArea, 
                             QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os
from models.product_model import ProductModel

class InventoryPanel(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.product_model = ProductModel(db)
        self.current_image_path = None
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Inventory Management")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        header_layout.addWidget(title)
        header_layout.addSpacing(10)
        header_layout.addStretch()
        
        # Show Add New Product button for both admin and staff
        if self.user_role in ['admin', 'staff']:
            add_btn = QPushButton("Add New Product")
            add_btn.setStyleSheet("""
                QPushButton {
                    background: #3498db;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #2980b9;
                }
            """)
            add_btn.clicked.connect(self.show_add_product_dialog)
            header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Filters
        filter_layout = QHBoxLayout()

        # Label with white background
        category_label = QLabel("Category:")
        category_label.setStyleSheet("""
            QLabel {    
                background-color: #f9fafb;
                color: black;
                padding: 5px 10px;
            }
        """)
        filter_layout.addWidget(category_label)

        # Combo box
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("""
            QComboBox {
                color: black;
                padding: 5px;
                background-color: white;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
            }
        """)
        self.category_combo.addItems(["All", "Food", "Accessories", "Medicine", "Toys", "Grooming"])
        self.category_combo.currentTextChanged.connect(self.filter_products)
        filter_layout.addWidget(self.category_combo)
        
        # Search
        search_label = QLabel("Search:")
        search_label.setStyleSheet("""
            QLabel {    
                background-color: #f9fafb;
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
        self.search_input.textChanged.connect(self.search_products)
        filter_layout.addWidget(self.search_input)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        layout.addSpacing(20)
        
        # Products table
        self.products_table = QTableWidget()
        # Show Actions column for both admin and staff
        self.products_table.setColumnCount(8 if self.user_role in ['admin', 'staff'] else 7)
        headers = ["ID", "Name", "Category", "Price", "Quantity", "Reorder Level", "Status"]
        if self.user_role in ['admin', 'staff']:
            headers.append("Actions")
        
        self.products_table.setHorizontalHeaderLabels(headers)
        
        # Style the table
        self.products_table.setStyleSheet("""
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
        
        # Set column resize modes
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Price
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Quantity
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Reorder Level
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Status
        
        if self.user_role in ['admin', 'staff']:
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Actions
        
        layout.addWidget(self.products_table)
        
        self.setLayout(layout)
    
    def load_products(self):
        products = self.product_model.get_all_products()
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.products_table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.products_table.setItem(row, 2, QTableWidgetItem(product['category']))
            self.products_table.setItem(row, 3, QTableWidgetItem(f"₱{product['price']:.2f}"))
            self.products_table.setItem(row, 4, QTableWidgetItem(str(product['quantity'])))
            self.products_table.setItem(row, 5, QTableWidgetItem(str(product['reorder_level'])))
            
            # Status with color coding
            status_item = QTableWidgetItem()
            if product['quantity'] == 0:
                status_item.setText("Out of Stock")
                status_item.setForeground(Qt.GlobalColor.white)
                status_item.setBackground(Qt.GlobalColor.darkRed)
            elif product['quantity'] <= product['reorder_level']:
                status_item.setText("Low Stock")
                status_item.setForeground(Qt.GlobalColor.black)
                status_item.setBackground(Qt.GlobalColor.yellow)
            else:
                status_item.setText("In Stock")
                status_item.setForeground(Qt.GlobalColor.darkGreen)
                status_item.setBackground(Qt.GlobalColor.white)
            
            self.products_table.setItem(row, 6, status_item)
            
            # Actions for admin and staff
            if self.user_role in ['admin', 'staff']:
                actions_widget = QWidget()
                actions_widget.setStyleSheet("background-color: white;")
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(5, 5, 5, 5)
                
                edit_btn = QPushButton("Edit")
                edit_btn.setMinimumHeight(20)
                edit_btn.setStyleSheet("""
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
                edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
                
                delete_btn = QPushButton("Delete")
                delete_btn.setMinimumHeight(20)
                delete_btn.setStyleSheet("""
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
                delete_btn.clicked.connect(lambda checked, p=product: self.delete_product(p['id']))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                actions_widget.setLayout(actions_layout)
                self.products_table.setCellWidget(row, 7, actions_widget)
    
    def search_products(self):
        search_text = self.search_input.text().lower()
        for row in range(self.products_table.rowCount()):
            match = False
            for col in range(3):  # Check ID, Name, Category
                item = self.products_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.products_table.setRowHidden(row, not match)
    
    def filter_products(self, category):
        if category == "All":
            for row in range(self.products_table.rowCount()):
                self.products_table.setRowHidden(row, False)
        else:
            for row in range(self.products_table.rowCount()):
                category_item = self.products_table.item(row, 2)
                if category_item and category_item.text() == category:
                    self.products_table.setRowHidden(row, False)
                else:
                    self.products_table.setRowHidden(row, True)
    
    def show_add_product_dialog(self):
        dialog = AddEditProductDialog(self.product_model)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def edit_product(self, product):
        dialog = AddEditProductDialog(self.product_model, product)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def delete_product(self, product_id):
        # Question dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Delete Product")
        msg_box.setText("Are you sure you want to delete this product?")
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
            if self.product_model.delete_product(product_id):
                # Success message
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText("Product deleted successfully")
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
                self.load_products()
            else:
                # Error message
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Error")
                error_msg.setText("Failed to delete product")
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

class AddEditProductDialog(QDialog):
    def __init__(self, product_model, product=None):
        super().__init__()
        self.product_model = product_model
        self.product = product
        self.current_image_path = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Add Product" if not self.product else "Edit Product")
        self.setModal(True)
        self.resize(600, 700)
        self.setStyleSheet("background-color: white; color: black;")
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create scroll area for the form
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
        
        # Create container widget for the form
        container_widget = QWidget()
        container_widget.setStyleSheet("background-color: white;")
        container_layout = QVBoxLayout()
        container_layout.setSpacing(20)
        
        # Image upload section
        image_group = QGroupBox("Product Image")
        image_group.setStyleSheet("""
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
        image_layout = QVBoxLayout()
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 200)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 10px;
                background: #f9fafb;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("Click 'Upload Image' to select a photo")
        
        upload_btn = QPushButton("Upload Image")
        upload_btn.setStyleSheet("""
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
        """)
        upload_btn.clicked.connect(self.upload_image)
        
        image_layout.addWidget(self.image_label, 0, Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(upload_btn, 0, Qt.AlignmentFlag.AlignCenter)
        image_group.setLayout(image_layout)
        container_layout.addWidget(image_group)
        
        # Basic Information Group
        basic_group = QGroupBox("Basic Information")
        basic_group.setStyleSheet("""
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
        basic_layout = QGridLayout()
        basic_layout.setHorizontalSpacing(20)
        basic_layout.setVerticalSpacing(10)
        
        # Row 0
        basic_layout.addWidget(QLabel("Name *:"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.name_input, 0, 1)
        
        basic_layout.addWidget(QLabel("Category *:"), 0, 2)
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Food", "Accessories", "Medicine", "Toys", "Grooming"])
        self.category_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.category_combo, 0, 3)
        
        # Row 1
        basic_layout.addWidget(QLabel("Price *:"), 1, 0)
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 10000)
        self.price_input.setPrefix("₱ ")
        self.price_input.setDecimals(2)
        self.price_input.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.price_input, 1, 1)
        
        basic_layout.addWidget(QLabel("Quantity *:"), 1, 2)
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 10000)
        self.quantity_input.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.quantity_input, 1, 3)
        
        # Row 2
        basic_layout.addWidget(QLabel("Reorder Level:"), 2, 0)
        self.reorder_input = QSpinBox()
        self.reorder_input.setRange(0, 1000)
        self.reorder_input.setValue(5)
        self.reorder_input.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.reorder_input, 2, 1)
        
        basic_group.setLayout(basic_layout)
        container_layout.addWidget(basic_group)
        
        # Description Group
        desc_group = QGroupBox("Description")
        desc_group.setStyleSheet("""
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
        desc_layout = QVBoxLayout()
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter product description, features, usage instructions...")
        self.description_input.setMaximumHeight(150)
        self.description_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        desc_layout.addWidget(self.description_input)
        
        desc_group.setLayout(desc_layout)
        container_layout.addWidget(desc_group)
        
        container_widget.setLayout(container_layout)
        scroll_area.setWidget(container_widget)
        main_layout.addWidget(scroll_area)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_product)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
        
        # Load product data if editing
        if self.product:
            self.load_product_data()
    
    def load_product_data(self):
        self.name_input.setText(self.product['name'])
        self.category_combo.setCurrentText(self.product['category'])
        self.price_input.setValue(float(self.product['price']))
        self.quantity_input.setValue(self.product['quantity'])
        self.reorder_input.setValue(self.product['reorder_level'])
        self.description_input.setText(self.product['description'] or '')
        
        # Load image if exists
        if self.product.get('image_path') and os.path.exists(self.product['image_path']):
            self.display_image(self.product['image_path'])
    
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Product Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
    
    def display_image(self, file_path):
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setText("")
    
    def save_product(self):
        # Validate required fields
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "Product name is required")
            return
        
        # Prepare product data
        product_data = {
            'name': self.name_input.text().strip(),
            'category': self.category_combo.currentText(),
            'price': self.price_input.value(),
            'quantity': self.quantity_input.value(),
            'reorder_level': self.reorder_input.value(),
            'description': self.description_input.toPlainText().strip(),
            'image_path': self.current_image_path or (self.product['image_path'] if self.product else None)
        }
        
        try:
            if self.product:
                # Update existing product
                if self.product_model.update_product(self.product['id'], product_data):
                    QMessageBox.information(self, "Success", "Product updated successfully")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update product")
            else:
                # Add new product
                if self.product_model.add_product(product_data):
                    QMessageBox.information(self, "Success", "Product added successfully")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add product")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
