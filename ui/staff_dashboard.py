from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedWidget, QFrame,
                             QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.panels.pet_management_panel import PetManagementPanel
from ui.panels.inventory_panel import InventoryPanel
from ui.panels.appointment_panel import AppointmentPanel
from ui.panels.sales_panel import SalesPanel
from ui.panels.attendance_panel import AttendancePanel
from ui.panels.customer_management_panel import CustomerManagementPanel
from ui.panels.pos_panel import POSPanel

class StaffDashboard(QMainWindow):
    logout_signal = pyqtSignal()
    
    def __init__(self, db, user_id, username):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.username = username
        self.init_ui()
        self.showFullScreen()
    
    def init_ui(self):
        self.setWindowTitle("Staff Dashboard - Pet Shop Management System")
        self.showMaximized()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.create_sidebar(main_layout)
        self.create_main_content(main_layout)
    
    def create_sidebar(self, main_layout):
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
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
                background: rgba(255,255,255,0.2);
                font-weight: bold;
            }
        """)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
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
        
        # Staff-specific navigation
        nav_buttons = [
            ("Pets Management", "pet_management"),
            ("Inventory", "inventory"),
            ("POS System", "pos"),
            ("Appointments", "appointments"),
            ("Sales", "sales"),
            ("Customer Lookup", "customer_management"),
            ("Attendance", "attendance")
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
        self.stacked_panels = QStackedWidget()
        self.stacked_panels.setStyleSheet("""
            QStackedWidget {
                background: #f8f9fa;
                border: none;
            }
        """)
        
        # Create staff-specific panels
        self.pet_panel = PetManagementPanel(self.db, 'staff')
        self.inventory_panel = InventoryPanel(self.db, 'staff')
        self.pos_panel = POSPanel(self.db, self.user_id, 'staff')
        self.appointment_panel = AppointmentPanel(self.db, 'staff')
        self.sales_panel = SalesPanel(self.db, 'staff')
        self.customer_panel = CustomerManagementPanel(self.db)
        self.attendance_panel = AttendancePanel(self.db, self.user_id)
        
        self.stacked_panels.addWidget(self.pet_panel)
        self.stacked_panels.addWidget(self.inventory_panel)
        self.stacked_panels.addWidget(self.pos_panel)
        self.stacked_panels.addWidget(self.appointment_panel)
        self.stacked_panels.addWidget(self.sales_panel)
        self.stacked_panels.addWidget(self.customer_panel)
        self.stacked_panels.addWidget(self.attendance_panel)
        
        main_layout.addWidget(self.stacked_panels, 1)
    
    def switch_panel(self):
        button = self.sender()
        panel_name = button.property('panel')
        
        for btn in self.nav_buttons_group:
            btn.setChecked(False)
        
        button.setChecked(True)
        
        panel_map = {
            'pet_management': 0,
            'inventory': 1,
            'pos': 2,
            'appointments': 3,
            'sales': 4,
            'customer_management': 5,
            'attendance': 6
        }
        
        if panel_name in panel_map:
            self.stacked_panels.setCurrentIndex(panel_map[panel_name])
    
    def logout(self):
        reply = QMessageBox.question(self, 'Confirm Logout', 
                                   'Are you sure you want to logout?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_signal.emit()