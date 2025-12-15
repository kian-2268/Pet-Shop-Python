from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QComboBox, QTextEdit, QDoubleSpinBox,
                             QSpinBox, QFileDialog, QMessageBox, QHeaderView,
                             QDialog, QDialogButtonBox, QGroupBox, QScrollArea, 
                             QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os
from models.pet_model import PetModel

class PetManagementPanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.pet_model = PetModel(db)
        self.current_image_path = None
        self.init_ui()
        self.load_pets()
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Pet Management")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        header_layout.addWidget(title)
        header_layout.addSpacing(10)
        header_layout.addStretch()
        
        add_btn = QPushButton("Add New Pet")
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
        add_btn.clicked.connect(self.show_add_pet_dialog)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
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

        # Combo box
        self.status_combo = QComboBox()
        self.status_combo.setStyleSheet("""
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
        self.status_combo.addItems(["All", "Available", "Sold", "Reserved", "Adopted"])
        self.status_combo.currentTextChanged.connect(self.filter_pets)
        filter_layout.addWidget(self.status_combo)
        
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
        self.search_input.setPlaceholderText("Search by name, species, breed...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                color: black;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        self.search_input.textChanged.connect(self.search_pets)
        filter_layout.addWidget(self.search_input)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        layout.addSpacing(20)
        
        # Pets table
        self.pets_table = QTableWidget()
        self.pets_table.setColumnCount(9)
        self.pets_table.setHorizontalHeaderLabels([
            "ID", "Name", "Species", "Breed", "Age", "Gender", "Price", "Status", "Actions"
        ])
        
        # Style the table
        self.pets_table.setStyleSheet("""
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
        header = self.pets_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Species
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Breed
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Age
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Gender
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Price
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Status
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)  # Actions
        
        layout.addWidget(self.pets_table)
        
        self.setLayout(layout)
    
    def load_pets(self):
        pets = self.pet_model.get_all_pets()
        self.pets_table.setRowCount(len(pets))
        
        for row, pet in enumerate(pets):
            self.pets_table.setItem(row, 0, QTableWidgetItem(str(pet['id'])))
            self.pets_table.setItem(row, 1, QTableWidgetItem(pet['name']))
            self.pets_table.setItem(row, 2, QTableWidgetItem(pet['species']))
            self.pets_table.setItem(row, 3, QTableWidgetItem(pet['breed'] or ''))
            self.pets_table.setItem(row, 4, QTableWidgetItem(str(pet['age'])))
            self.pets_table.setItem(row, 5, QTableWidgetItem(pet['gender']))
            self.pets_table.setItem(row, 6, QTableWidgetItem(f"₱{pet['price']:.2f}"))
            
            # Status with color coding
            status_item = QTableWidgetItem(pet['status'])
            if pet['status'] == 'Available':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif pet['status'] == 'Sold':
                status_item.setForeground(Qt.GlobalColor.blue)
            elif pet['status'] == 'Reserved':
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            elif pet['status'] == 'Adopted':
                status_item.setForeground(Qt.GlobalColor.darkMagenta)
            self.pets_table.setItem(row, 7, status_item)
            
            # Actions
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
            edit_btn.clicked.connect(lambda checked, p=pet: self.edit_pet(p))
            
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
            delete_btn.clicked.connect(lambda checked, p=pet: self.delete_pet(p['id']))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            actions_widget.setLayout(actions_layout)
            self.pets_table.setCellWidget(row, 8, actions_widget)
    
    def search_pets(self):
        search_text = self.search_input.text().lower()
        for row in range(self.pets_table.rowCount()):
            match = False
            for col in range(7):  # Check first 7 columns
                item = self.pets_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.pets_table.setRowHidden(row, not match)
    
    def filter_pets(self, status):
        if status == "All":
            for row in range(self.pets_table.rowCount()):
                self.pets_table.setRowHidden(row, False)
        else:
            for row in range(self.pets_table.rowCount()):
                status_item = self.pets_table.item(row, 7)
                if status_item and status_item.text() == status:
                    self.pets_table.setRowHidden(row, False)
                else:
                    self.pets_table.setRowHidden(row, True)
    
    def show_add_pet_dialog(self):
        dialog = AddEditPetDialog(self.pet_model, self.user_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_pets()
    
    def edit_pet(self, pet):
        dialog = AddEditPetDialog(self.pet_model, self.user_id, pet)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_pets()
    
    def delete_pet(self, pet_id):
        # Question dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Delete Pet")
        msg_box.setText("Are you sure you want to delete this pet?")
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
            if self.pet_model.delete_pet(pet_id):
                # Success message
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText("Pet deleted successfully")
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
                self.load_pets()
            else:
                # Error message
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Error")
                error_msg.setText("Failed to delete pet")
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

class AddEditPetDialog(QDialog):
    def __init__(self, pet_model, user_id, pet=None):
        super().__init__()
        self.pet_model = pet_model
        self.user_id = user_id
        self.pet = pet
        self.current_image_path = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Add Pet" if not self.pet else "Edit Pet")
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
        image_group = QGroupBox("Pet Image")
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
        
        basic_layout.addWidget(QLabel("Species *:"), 0, 2)
        self.species_input = QLineEdit()
        self.species_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.species_input, 0, 3)
        
        # Row 1
        basic_layout.addWidget(QLabel("Breed:"), 1, 0)
        self.breed_input = QLineEdit()
        self.breed_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.breed_input, 1, 1)
        
        basic_layout.addWidget(QLabel("Age:"), 1, 2)
        self.age_input = QSpinBox()
        self.age_input.setRange(0, 50)
        self.age_input.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.age_input, 1, 3)
        
        # Row 2
        basic_layout.addWidget(QLabel("Gender *:"), 2, 0)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Male", "Female", "Unknown"])
        self.gender_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.gender_combo, 2, 1)
        
        basic_layout.addWidget(QLabel("Price *:"), 2, 2)
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
        basic_layout.addWidget(self.price_input, 2, 3)
        
        # Row 3
        basic_layout.addWidget(QLabel("Status:"), 3, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Available", "Sold", "Reserved", "Adopted"])
        self.status_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        basic_layout.addWidget(self.status_combo, 3, 1)
        
        basic_group.setLayout(basic_layout)
        container_layout.addWidget(basic_group)
        
        # Health Information Group
        health_group = QGroupBox("Health Information")
        health_group.setStyleSheet("""
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
        health_layout = QGridLayout()
        health_layout.setHorizontalSpacing(20)
        health_layout.setVerticalSpacing(10)
        
        health_layout.addWidget(QLabel("Health Status:"), 0, 0)
        self.health_input = QLineEdit()
        self.health_input.setPlaceholderText("e.g., Healthy, Under Treatment")
        self.health_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        health_layout.addWidget(self.health_input, 0, 1, 1, 3)
        
        health_layout.addWidget(QLabel("Vaccination:"), 1, 0)
        self.vaccination_input = QLineEdit()
        self.vaccination_input.setPlaceholderText("e.g., Fully Vaccinated, Needs Rabies")
        self.vaccination_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9fafb;
            }
        """)
        health_layout.addWidget(self.vaccination_input, 1, 1, 1, 3)
        
        health_group.setLayout(health_layout)
        container_layout.addWidget(health_group)
        
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
        self.description_input.setPlaceholderText("Enter pet description, personality, special needs...")
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
        button_box.accepted.connect(self.save_pet)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
        
        # Load pet data if editing
        if self.pet:
            self.load_pet_data()
    
    def load_pet_data(self):
        self.name_input.setText(self.pet['name'])
        self.species_input.setText(self.pet['species'])
        self.breed_input.setText(self.pet['breed'] or '')
        self.age_input.setValue(self.pet['age'] or 0)
        self.gender_combo.setCurrentText(self.pet['gender'])
        self.price_input.setValue(float(self.pet['price']))
        self.status_combo.setCurrentText(self.pet['status'])
        self.health_input.setText(self.pet['health_status'] or '')
        self.vaccination_input.setText(self.pet['vaccination_status'] or '')
        self.description_input.setText(self.pet['description'] or '')
        
        # Load image if exists
        if self.pet.get('image_path') and os.path.exists(self.pet['image_path']):
            self.display_image(self.pet['image_path'])
    
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Pet Image", "", 
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
    
    def save_pet(self):
        # Validate required fields
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "Pet name is required")
            return
        
        if not self.species_input.text().strip():
            QMessageBox.warning(self, "Error", "Species is required")
            return
        
        # Prepare pet data
        pet_data = {
            'name': self.name_input.text().strip(),
            'species': self.species_input.text().strip(),
            'breed': self.breed_input.text().strip(),
            'age': self.age_input.value(),
            'gender': self.gender_combo.currentText(),
            'price': self.price_input.value(),
            'status': self.status_combo.currentText(),
            'health_status': self.health_input.text().strip(),
            'vaccination_status': self.vaccination_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'image_path': self.current_image_path or (self.pet['image_path'] if self.pet else None)
        }
        
        try:
            if self.pet:
                # Update existing pet
                if self.pet_model.update_pet(self.pet['id'], pet_data):
                    QMessageBox.information(self, "Success", "Pet updated successfully")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update pet")
            else:
                # Add new pet - FIXED: Added created_by parameter
                if self.pet_model.add_pet(pet_data, self.user_id):
                    QMessageBox.information(self, "Success", "Pet added successfully")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add pet")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
