from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QComboBox, QTextEdit, QDoubleSpinBox,
                             QSpinBox, QFileDialog, QMessageBox, QHeaderView,
                             QDialog, QFormLayout, QDialogButtonBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
import os
from models.pet_model import PetModel

class PetManagementPanel(QWidget):
    def __init__(self, db, user_role):
        super().__init__()
        self.db = db
        self.user_role = user_role
        self.pet_model = PetModel(db)
        self.current_image_path = None
        self.init_ui()
        self.load_pets()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Pet Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search pets...")
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
        self.search_input.textChanged.connect(self.search_pets)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Available", "Sold", "Reserved", "Adopted"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 14px;
                min-width: 150px;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.filter_pets)
        
        add_btn = QPushButton("Add New Pet")
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
        add_btn.clicked.connect(self.show_add_pet_dialog)
        
        controls_layout.addWidget(QLabel("Search:"))
        controls_layout.addWidget(self.search_input)
        controls_layout.addWidget(QLabel("Status:"))
        controls_layout.addWidget(self.filter_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(add_btn)
        
        layout.addLayout(controls_layout)
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
                gridline-color: #e1e1e1;
            }
            QHeaderView::section {
                background: #f8f9fa;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        self.pets_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
            self.pets_table.setItem(row, 6, QTableWidgetItem(f"${pet['price']:.2f}"))
            self.pets_table.setItem(row, 7, QTableWidgetItem(pet['status']))
            
            # Actions
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
            edit_btn.clicked.connect(lambda checked, p=pet: self.edit_pet(p))
            
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
        dialog = AddEditPetDialog(self.pet_model, self.user_id if hasattr(self, 'user_id') else 1)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_pets()
    
    def edit_pet(self, pet):
        dialog = AddEditPetDialog(self.pet_model, self.user_id if hasattr(self, 'user_id') else 1, pet)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_pets()
    
    def delete_pet(self, pet_id):
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                   'Are you sure you want to delete this pet?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.pet_model.delete_pet(pet_id):
                QMessageBox.information(self, 'Success', 'Pet deleted successfully')
                self.load_pets()
            else:
                QMessageBox.warning(self, 'Error', 'Failed to delete pet')

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
        self.resize(500, 600)
        
        layout = QVBoxLayout()
        
        # Image upload section
        image_group = QGroupBox("Pet Image")
        image_layout = QVBoxLayout()
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 200)
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
        self.species_input = QLineEdit()
        self.breed_input = QLineEdit()
        self.age_input = QSpinBox()
        self.age_input.setRange(0, 50)
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Male", "Female", "Unknown"])
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 10000)
        self.price_input.setPrefix("$ ")
        self.price_input.setDecimals(2)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Available", "Sold", "Reserved", "Adopted"])
        
        self.health_input = QLineEdit()
        self.vaccination_input = QLineEdit()
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        
        # Style inputs
        for widget in [self.name_input, self.species_input, self.breed_input, 
                      self.health_input, self.vaccination_input]:
            widget.setStyleSheet("""
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
        form_layout.addRow("Species *:", self.species_input)
        form_layout.addRow("Breed:", self.breed_input)
        form_layout.addRow("Age:", self.age_input)
        form_layout.addRow("Gender *:", self.gender_combo)
        form_layout.addRow("Price *:", self.price_input)
        form_layout.addRow("Status:", self.status_combo)
        form_layout.addRow("Health Status:", self.health_input)
        form_layout.addRow("Vaccination:", self.vaccination_input)
        form_layout.addRow("Description:", self.description_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_pet)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
        
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
        if self.pet['image_path'] and os.path.exists(self.pet['image_path']):
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
                # Add new pet
                if self.pet_model.add_pet(pet_data, self.user_id):
                    QMessageBox.information(self, "Success", "Pet added successfully")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add pet")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")