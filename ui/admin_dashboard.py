from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedWidget, QFrame,
                             QMessageBox, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from ui.panels.pet_management_panel import PetManagementPanel
from ui.panels.inventory_panel import InventoryPanel
from ui.panels.staff_management_panel import StaffManagementPanel
from ui.panels.customer_management_panel import CustomerManagementPanel
from ui.panels.appointment_panel import AppointmentPanel
from ui.panels.sales_panel import SalesPanel
from ui.panels.reports_panel import ReportsPanel
from ui.panels.adoption_panel import AdoptionPanel

class AdminDashboard(QMainWindow):
    logout_signal = pyqtSignal()
    
    def __init__(self, db, user_id, username):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.username = username
        self.init_ui()
        self.showFullScreen()
    
    def init_ui(self):
        self.setWindowTitle("Admin Dashboard - Pet Shop Management System")
        self.showMaximized()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.create_sidebar(main_layout)
        
        # Create main content area
        self.create_main_content(main_layout)
    
    def create_sidebar(self, main_layout):
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #34495e);
                min-width: 250px;
                max-width: 250px;
            }
            QPushButton {
                background: transparent;
                color: white;
                padding: 15px 20px;
                border: none;
                text-align: left;
                font-size: 14px;
                border-radius: 8px;
                margin: 2px 5px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
            }
            QPushButton:checked {
                background: #3498db;
                font-weight: bold;
            }
        """)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # Welcome section
        welcome_label = QLabel(f"Welcome, {self.username}")
        welcome_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                border-bottom: 1px solid rgba(255,255,255,0.2);
                margin-bottom: 10px;
            }
        """)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(welcome_label)
        
        sidebar_layout.addSpacing(20)
        
        # Navigation buttons
        nav_buttons = [
            ("Pets Management", "pet_management"),
            ("Inventory", "inventory"),
            ("Staff Management", "staff_management"),
            ("Customer Management", "customer_management"),
            ("Appointments", "appointments"),
            ("Sales", "sales"),
            ("Adoption", "adoption"),
            ("Reports & Analytics", "reports")
        ]
        
        self.nav_buttons_group = []
        for text, panel_name in nav_buttons:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty('panel', panel_name)
            btn.clicked.connect(self.switch_panel)
            sidebar_layout.addWidget(btn)
            self.nav_buttons_group.append(btn)
        
        sidebar_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar)
    
    def create_main_content(self, main_layout):
        # Create stacked widget for panels
        self.stacked_panels = QStackedWidget()
        self.stacked_panels.setStyleSheet("""
            QStackedWidget {
                background: #f8f9fa;
                border: none;
            }
        """)
        
        # Create and add panels
        self.pet_panel = PetManagementPanel(self.db, 'admin')
        self.inventory_panel = InventoryPanel(self.db, 'admin')
        self.staff_panel = StaffManagementPanel(self.db)
        self.customer_panel = CustomerManagementPanel(self.db)
        self.appointment_panel = AppointmentPanel(self.db, 'admin')
        self.sales_panel = SalesPanel(self.db, 'admin')
        self.adoption_panel = AdoptionPanel(self.db, 'admin')
        self.reports_panel = ReportsPanel(self.db)
        
        self.stacked_panels.addWidget(self.pet_panel)
        self.stacked_panels.addWidget(self.inventory_panel)
        self.stacked_panels.addWidget(self.staff_panel)
        self.stacked_panels.addWidget(self.customer_panel)
        self.stacked_panels.addWidget(self.appointment_panel)
        self.stacked_panels.addWidget(self.sales_panel)
        self.stacked_panels.addWidget(self.adoption_panel)
        self.stacked_panels.addWidget(self.reports_panel)
        
        main_layout.addWidget(self.stacked_panels, 1)
    
    def switch_panel(self):
        button = self.sender()
        panel_name = button.property('panel')
        
        # Uncheck all buttons
        for btn in self.nav_buttons_group:
            btn.setChecked(False)
        
        # Check clicked button
        button.setChecked(True)
        
        # Switch to corresponding panel
        panel_map = {
            'pet_management': 0,
            'inventory': 1,
            'staff_management': 2,
            'customer_management': 3,
            'appointments': 4,
            'sales': 5,
            'adoption': 6,
            'reports': 7
        }
        
        if panel_name in panel_map:
            self.stacked_panels.setCurrentIndex(panel_map[panel_name])
    
    def logout(self):
        reply = QMessageBox.question(self, 'Confirm Logout', 
                                   'Are you sure you want to logout?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_signal.emit()