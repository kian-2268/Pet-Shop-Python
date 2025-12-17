from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QComboBox, QLineEdit,
                             QMessageBox, QGroupBox, QDialog, QFormLayout,
                             QDialogButtonBox, QTextEdit, QGridLayout)
from PyQt6.QtCore import Qt
import os
from PyQt6.QtGui import QPixmap
from models.pet_model import PetModel
from models.adoption_model import AdoptionModel
from models.cart_model import CartModel

class CustomerPetsPanel(QWidget):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.pet_model = PetModel(db)
        self.adoption_model = AdoptionModel(db)
        self.cart_model = CartModel(db)
        self.all_pets = [] 
        self.init_ui()
        self.load_pets()
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Available Pets")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search and filter
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search pets by name, breed, or description...")
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
        self.search_input.textChanged.connect(self.search_pets)
        
        self.species_combo = QComboBox()
        self.species_combo.addItems(["All Species", "Dog", "Cat", "Bird", "Rabbit", "Other"])
        self.species_combo.setStyleSheet("""
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
        self.species_combo.currentTextChanged.connect(self.filter_pets)
        
        # Price filter
        self.price_combo = QComboBox()
        self.price_combo.addItems(["Any Price", "Under ₱100", "₱100 - ₱300", "₱300 - ₱500", "Over ₱500"])
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
        self.price_combo.currentTextChanged.connect(self.filter_pets)
        
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
        header_layout.addWidget(self.species_combo)
        header_layout.addWidget(self.price_combo)
        header_layout.addWidget(clear_btn)
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Pets grid
        self.pets_scroll = QScrollArea()
        self.pets_widget = QWidget()
        self.pets_layout = QHBoxLayout(self.pets_widget)
        self.pets_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.pets_scroll.setWidget(self.pets_widget)
        self.pets_scroll.setWidgetResizable(True)
        
        layout.addWidget(self.pets_scroll)
        self.setLayout(layout)
    
    def load_pets(self):
        self.all_pets = self.pet_model.get_all_pets('Available')
        self.apply_filters()
    
    def apply_filters(self):
        filtered_pets = self.all_pets.copy()
        
        # Apply search filter
        search_text = self.search_input.text().strip().lower()
        if search_text:
            filtered_pets = [pet for pet in filtered_pets if 
                           search_text in pet['name'].lower() or 
                           (pet['breed'] and search_text in pet['breed'].lower()) or
                           (pet['description'] and search_text in pet['description'].lower())]
        
        # Apply species filter
        species_filter = self.species_combo.currentText()
        if species_filter != "All Species":
            filtered_pets = [pet for pet in filtered_pets if pet['species'] == species_filter]
        
        # Apply price filter
        price_filter = self.price_combo.currentText()
        if price_filter == "Under ₱100":
            filtered_pets = [pet for pet in filtered_pets if pet['price'] < 100]
        elif price_filter == "₱100 - ₱300":
            filtered_pets = [pet for pet in filtered_pets if 100 <= pet['price'] <= 300]
        elif price_filter == "₱300 - ₱500":
            filtered_pets = [pet for pet in filtered_pets if 300 <= pet['price'] <= 500]
        elif price_filter == "Over ₱500":
            filtered_pets = [pet for pet in filtered_pets if pet['price'] > 500]
        
        self.display_pets(filtered_pets)
    
    def search_pets(self):
        # Handle search text changes
        self.apply_filters()
    
    def filter_pets(self):
        # Handle filter changes
        self.apply_filters()
    
    def clear_filters(self):
        # Clear all filters and reset to default
        self.search_input.clear()
        self.species_combo.setCurrentText("All Species")
        self.price_combo.setCurrentText("Any Price")
        self.apply_filters()
    
    def display_pets(self, pets):
        # Clear existing pets
        for i in reversed(range(self.pets_layout.count())): 
            widget = self.pets_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
    
        if not pets:
            # Show no results message
            no_results = QLabel("No pets found matching your criteria.")
            no_results.setStyleSheet("color: #7f8c8d; font-size: 16px; text-align: center;")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pets_layout.addWidget(no_results)
            return
    
        # Create a grid widget using QGridLayout (like POS system)
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
        num_rows = (len(pets) + 1) // 4  # Integer division for rows
    
        # Add pets to grid
        for i, pet in enumerate(pets):
            row = i // 4
            col = i % 4
            pet_card = self.create_pet_card(pet)
            container_layout.addWidget(pet_card, row, col)
    
        # Add container to grid widget
        grid_layout.addWidget(container)
        self.pets_layout.addWidget(grid_widget)

    def create_pet_card(self, pet):
        card = QGroupBox()
        card.setFixedSize(450, 500)
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
        layout.setSpacing(12)
        
        # Pet image
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
        
        if pet['image_path'] and os.path.exists(pet['image_path']):
            pixmap = QPixmap(pet['image_path'])
            scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
        else:
            image_label.setText("No Image Available")
        
        layout.addWidget(image_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Pet info
        name_label = QLabel(pet['name'])
        name_label.setStyleSheet("background-color: white; font-weight: bold; font-size: 18px; color: black;")
        layout.addWidget(name_label)

        breed_label = QLabel(f"{pet['species']} • {pet['breed'] or 'Mixed'}")
        breed_label.setStyleSheet("background-color: white; color: black; font-size: 14px;")
        layout.addWidget(breed_label)

        details_layout = QHBoxLayout()
        details_layout.setSpacing(10)
        details_layout.setContentsMargins(0, 0, 0, 0)

        age_label = QLabel(f"Age: {pet['age']} years")
        age_label.setFixedWidth(120) 
        age_label.setStyleSheet("""
            QLabel {
                color: black;
                font-size: 14px;
                background-color: white;
                margin: 0px;
                padding: 0px;
            }
        """)

        gender_label = QLabel(f"Gender: {pet['gender']}")
        gender_label.setFixedWidth(120)  # Same fixed width
        gender_label.setStyleSheet("""
            QLabel {
                color: black;
                font-size: 14px;
                background-color: white;
                margin: 0px;
                padding: 0px;
            }
        """)

        details_layout.addWidget(age_label)
        details_layout.addWidget(gender_label)
        details_layout.addStretch()
        layout.addLayout(details_layout)
        
        health_label = QLabel(f"Health: {pet['health_status'] or 'Good'}")
        health_label.setStyleSheet("background-color: white; color: #27ae60; font-size: 12px;")
        layout.addWidget(health_label)
        
        if pet['description']:
            desc_label = QLabel(pet['description'])
            desc_label.setStyleSheet("background-color: white; color: black; font-size: 12px;")
            desc_label.setWordWrap(True)
            desc_label.setMaximumHeight(40)
            layout.addWidget(desc_label)
        
        price_label = QLabel(f"₱{pet['price']:.2f}")
        price_label.setStyleSheet("background-color: white; color: #e74c3c; font-size: 20px; font-weight: bold;")
        layout.addWidget(price_label)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        adopt_btn = QPushButton("Adopt")
        adopt_btn.setStyleSheet("""
            QPushButton {
                background: #e67e22;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #f9d162;
            }
        """)
        adopt_btn.clicked.connect(lambda: self.request_adoption(pet))
        
        buy_btn = QPushButton("Add to Cart")
        buy_btn.setStyleSheet("""
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
        buy_btn.clicked.connect(lambda: self.add_to_cart(pet))
        
        buttons_layout.addWidget(adopt_btn)
        buttons_layout.addWidget(buy_btn)
        layout.addLayout(buttons_layout)
        
        card.setLayout(layout)
        return card
    
    def request_adoption(self, pet):
        dialog = AdoptionRequestDialog(self.adoption_model, self.user_id, pet)
        dialog.exec()
    
    def add_to_cart(self, pet):
        try:
            result = self.cart_model.add_to_cart(self.user_id, 'pet', pet['id'], 1)
            if result:
                # Create styled message box
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Success")
                msg_box.setText(f"{pet['name']} added to cart!")
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: white;
                    }
                    QMessageBox QLabel {
                        color: black;
                        background-color: white;
                    }
                    QPushButton {
                        background: #5ab9ea;
                        color: white;
                        padding: 8px 15px;
                        border: none;
                        border-radius: 5px;
                        font-weight: bold;
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
                msg_box.setText("Failed to add pet to cart")
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
        """Find and refresh the cart panel - same as in CustomerProductsPanel"""
        # Method 1: If CustomerDashboard has a direct reference to cart_panel
        parent = self.parent()
        while parent:
            if hasattr(parent, 'cart_panel'):
                parent.cart_panel.refresh_cart()
                return True
            parent = parent.parent()
        
        # Method 2: If using tab widget
        parent = self.parent()
        while parent:
            if hasattr(parent, 'tab_widget'):
                for i in range(parent.tab_widget.count()):
                    widget = parent.tab_widget.widget(i)
                    if hasattr(widget, 'refresh_cart'):
                        widget.refresh_cart()
                        return True
            parent = parent.parent()
        
        # Method 3: Search through all windows
        from PyQt6.QtWidgets import QApplication
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'cart_panel'):
                widget.cart_panel.refresh_cart()
                return True
        
        return False

class AdoptionRequestDialog(QDialog):
    def __init__(self, adoption_model, customer_id, pet):
        super().__init__()
        self.adoption_model = adoption_model
        self.customer_id = customer_id
        self.pet = pet
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Adopt {self.pet['name']}")
        self.setModal(True)
        self.setStyleSheet("background-color: white; color: black;")
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Pet info
        info_group = QGroupBox("Pet Information")
        info_layout = QFormLayout()
        info_layout.addRow("Name:", QLabel(self.pet['name']))
        info_layout.addRow("Species:", QLabel(self.pet['species']))
        info_layout.addRow("Breed:", QLabel(self.pet['breed'] or 'Mixed'))
        info_layout.addRow("Age:", QLabel(str(self.pet['age'])))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Adoption details
        details_group = QGroupBox("Adoption Details")
        details_layout = QFormLayout()
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Tell us why you'd like to adopt this pet...")
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                border-color: white;
                color: black;
            }
        """)
        
        details_layout.addRow("Notes:", self.notes_input)
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.submit_adoption)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def submit_adoption(self):
        notes = self.notes_input.toPlainText().strip()
    
        # Create adoption request
        result = self.adoption_model.create_adoption_request(self.customer_id, self.pet['id'], notes)
        
        if result:
            # Success message
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Adoption Request Submitted")
            msg_box.setText("Your adoption request has been submitted for review!")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: white;
                }
                QMessageBox QLabel {
                    color: black;
                    background-color: white;
                }
                QMessageBox QPushButton {
                    background-color: #e67e22;
                    color: white;
                    padding: 8px 15px;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #f9d162;
                }
            """)
        
            msg_box.exec()
            self.accept()
        else:
            # Error message
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Adoption Failed")
            msg_box.setText("Failed to submit your adoption request")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: black;
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
