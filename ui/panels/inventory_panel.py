from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QComboBox, QTextEdit, QDoubleSpinBox,
                             QSpinBox, QFileDialog, QMessageBox, QHeaderView,
                             QDialog, QFormLayout, QDialogButtonBox, QGroupBox)
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
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Inventory Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        self.search_input.textChanged.connect(self.search_products)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All", "Food", "Accessories", "Medicine", "Toys", "Grooming"])
        self.category_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
                min-width: 150px;
            }
        """)
        self.category_combo.currentTextChanged.connect(self.filter_products)
        
        if self.user_role == 'admin':
            add_btn = QPushButton("Add New Product")
            add_btn.setStyleSheet("""
                QPushButton {
                    background: #28a745;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #218838;
                }
            """)
            add_btn.clicked.connect(self.show_add_product_dialog)
            controls_layout.addWidget(add_btn)
        
        controls_layout.addWidget(QLabel("Search:"))
        controls_layout.addWidget(self.search_input)
        controls_layout.addWidget(QLabel("Category:"))
        controls_layout.addWidget(self.category_combo)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        layout.addSpacing(20)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(8 if self.user_role == 'admin' else 7)
        headers = ["ID", "Name", "Category", "Price", "Quantity", "Reorder Level", "Status"]
        if self.user_role == 'admin':
            headers.append("Actions")
        
        self.products_table.setHorizontalHeaderLabels(headers)
        
        self.products_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e1e1e1;
                border-radius: 8px;
                background: white;
                gridline-color: #e1e1e1;
            }
            QHeaderView::section {
                background: #f8f9fa;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.products_table)
        
        self.setLayout(layout)
    
    def load_products(self):
        products = self.product_model.get_all_products()
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.products_table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.products_table.setItem(row, 2, QTableWidgetItem(product['category']))
            self.products_table.setItem(row, 3, QTableWidgetItem(f"${product['price']:.2f}"))
            self.products_table.setItem(row, 4, QTableWidgetItem(str(product['quantity'])))
            self.products_table.setItem(row, 5, QTableWidgetItem(str(product['reorder_level'])))
            
            # Status with color coding
            status_item = QTableWidgetItem()
            if product['quantity'] == 0:
                status_item.setText("Out of Stock")
                status_item.setBackground(Qt.GlobalColor.red)
                status_item.setForeground(Qt.GlobalColor.white)
            elif product['quantity'] <= product['reorder_level']:
                status_item.setText("Low Stock")
                status_item.setBackground(Qt.GlobalColor.yellow)
            else:
                status_item.setText("In Stock")
                status_item.setBackground(Qt.GlobalColor.green)
                status_item.setForeground(Qt.GlobalColor.white)
            
            self.products_table.setItem(row, 6, status_item)
            
            # Actions for admin
            if self.user_role == 'admin':
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(5, 5, 5, 5)
                
                edit_btn = QPushButton("Edit")
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background: #007bff;
                        color: white;
                        padding: 5px 10px;
                        border: none;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background: #0056b3;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
                
                delete_btn = QPushButton("Delete")
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
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                   'Are you sure you want to delete this product?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.product_model.delete_product(product_id):
                QMessageBox.information(self, 'Success', 'Product deleted successfully')
                self.load_products()
            else:
                QMessageBox.warning(self, 'Error', 'Failed to delete product')

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
        self.resize(500, 500)
        
        layout = QVBoxLayout()
        
        # Image upload section
        image_group = QGroupBox("Product Image")
        image_layout = QVBoxLayout()
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(150, 150)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 10px;
                background: #f8f9fa;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("No image selected")
        
        upload_btn = QPushButton("Upload Image")
        upload_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        upload_btn.clicked.connect(self.upload_image)
        
        image_layout.addWidget(self.image_label, 0, Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(upload_btn, 0, Qt.AlignmentFlag.AlignCenter)
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.name_input = QLineEdit()
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Food", "Accessories", "Medicine", "Toys", "Grooming"])
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 10000)
        self.price_input.setPrefix("$ ")
        self.price_input.setDecimals(2)
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 10000)
        
        self.reorder_input = QSpinBox()
        self.reorder_input.setRange(0, 1000)
        self.reorder_input.setValue(5)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        
        # Style inputs
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        self.description_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        form_layout.addRow("Name *:", self.name_input)
        form_layout.addRow("Category *:", self.category_combo)
        form_layout.addRow("Price *:", self.price_input)
        form_layout.addRow("Quantity *:", self.quantity_input)
        form_layout.addRow("Reorder Level:", self.reorder_input)
        form_layout.addRow("Description:", self.description_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_product)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
        
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
        if self.product['image_path'] and os.path.exists(self.product['image_path']):
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
            scaled_pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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