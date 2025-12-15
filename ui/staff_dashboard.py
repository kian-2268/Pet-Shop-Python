from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedWidget, QFrame,
                             QMessageBox, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPalette, QBrush, QPixmap
import os
from ui.panels.pet_management_panel import PetManagementPanel
from ui.panels.inventory_panel import InventoryPanel
from ui.panels.appointment_panel import AppointmentPanel
from ui.panels.sales_panel import SalesPanel
from ui.panels.attendance_panel import AttendancePanel
from ui.panels.customer_management_panel import CustomerManagementPanel
from ui.panels.pos_panel import POSPanel
from ui.panels.surrender_management_panel import SurrenderManagementPanel

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
        sidebar.setFixedWidth(250)
        
        # Set solid orange background color (same as admin dashboard)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #e67e22;
                border: none;
            }
        """)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)

        # Top bar with welcome message only (same style as admin)
        top_bar = QWidget()
        top_bar.setStyleSheet("background: rgba(0, 0, 0, 0.4); border-radius: 10px;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(10, 10, 10, 10)
        
        # Welcome text
        welcome_widget = QWidget()
        welcome_widget.setStyleSheet("background: transparent;")
        welcome_layout = QHBoxLayout()
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        welcome_layout.setSpacing(8)

        # Icon
        icon_label = QLabel()
        try:
            # Try to load the same icon as admin dashboard
            pixmap = QPixmap("system_images/p3.png")
            if pixmap.isNull():
                # Try alternative
                pixmap = QPixmap("system_images/p3.png")
    
            if not pixmap.isNull():
                pixmap = pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
        except:
            pass  # No icon if image not found

        welcome_layout.addWidget(icon_label)

        # Text
        welcome_label = QLabel(f"Welcome, {self.username}!")
        welcome_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addStretch()

        welcome_widget.setLayout(welcome_layout)
        top_bar_layout.addWidget(welcome_widget)
        top_bar_layout.addStretch()
        
        sidebar_layout.addWidget(top_bar)
        sidebar_layout.addSpacing(20)
        
        # Staff-specific navigation buttons
        nav_buttons = [
            (" Pets Management", "pet_management", "system_images/pets.png"),
            (" Inventory", "inventory", "system_images/products.png"),
            (" POS System", "pos", "system_images/pos.png"),
            (" Appointments", "appointments", "system_images/appointment.png"),
            (" Sales", "sales", "system_images/sales.png"),
            (" Customer Lookup", "customer_management", "system_images/customer.png"),
            (" Attendance", "attendance", "system_images/attendance.png"),
            (" Surrender Requests", "surrender", "system_images/surrender.png") 
        ]
        
        self.nav_buttons_group = []
        for text, panel_name, icon_path in nav_buttons:
            btn = QPushButton(text)
            
            # Set icon if available 
            try:
                if os.path.exists(icon_path):
                    icon = QIcon(icon_path)
                    btn.setIcon(icon)
                    btn.setIconSize(QSize(20, 20))
                else:
                    # Fallback to emoji icons if image not found
                    emoji_icons = {
                        'pet_management': '🐾',
                        'inventory': '📦',
                        'pos': '💰',
                        'appointments': '📅',
                        'sales': '💵',
                        'customer_management': '👥',
                        'attendance': '📋',
                        'surrender': '💔'  
                    }
                    if panel_name in emoji_icons:
                        btn.setText(f"{emoji_icons[panel_name]}  {text}")
            except:
                pass  # Fallback to text-only
            
            btn.setCheckable(True)
            btn.setProperty('panel', panel_name)
            btn.clicked.connect(self.switch_panel)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.15);
                    color: black;
                    padding: 15px 20px;
                    border: none;
                    text-align: left;
                    font-size: 14px;
                    border-radius: 8px;
                    margin: 2px 5px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.25);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }
                QPushButton:checked {
                    background: rgba(255, 255, 255, 0.3);
                    font-weight: bold;
                    border: 1px solid rgba(255, 255, 255, 0.4);
                }
            """)
            sidebar_layout.addWidget(btn)
            self.nav_buttons_group.append(btn)
        
        sidebar_layout.addStretch()
        
        logout_btn = QPushButton(" Logout")
        
        # Set icon
        try:
            if os.path.exists("system_images/logout.png"):
                icon = QIcon("system_images/logout.png")
                logout_btn.setIcon(icon)
                logout_btn.setIconSize(QSize(20, 20))
            else:
                # Fallback to emoji if image not found
                logout_btn.setText("🚪  Logout")
        except:
            logout_btn.setText("🚪  Logout")
        
        logout_btn.setStyleSheet("""
            QPushButton {
                background: rgba(231, 76, 60, 0.8);
                color: white;
                padding: 12px 15px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                margin: 5px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                text-align: center;
            }
            QPushButton:hover {
                background: rgba(192, 57, 43, 0.9);
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
        
        # Create staff-specific panels
        self.pet_panel = PetManagementPanel(self.db, 'staff')
        self.inventory_panel = InventoryPanel(self.db, 'staff')
        self.pos_panel = POSPanel(self.db, self.user_id, 'staff')
        self.appointment_panel = AppointmentPanel(self.db, 'staff')
        self.sales_panel = SalesPanel(self.db, 'staff')
        self.customer_panel = CustomerManagementPanel(self.db)
        self.attendance_panel = AttendancePanel(self.db, self.user_id)
        self.surrender_panel = SurrenderManagementPanel(self.db, self.user_id) 
        
        self.stacked_panels.addWidget(self.pet_panel)
        self.stacked_panels.addWidget(self.inventory_panel)
        self.stacked_panels.addWidget(self.pos_panel)
        self.stacked_panels.addWidget(self.appointment_panel)
        self.stacked_panels.addWidget(self.sales_panel)
        self.stacked_panels.addWidget(self.customer_panel)
        self.stacked_panels.addWidget(self.attendance_panel)
        self.stacked_panels.addWidget(self.surrender_panel) 
        
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
            'pos': 2,
            'appointments': 3,
            'sales': 4,
            'customer_management': 5,
            'attendance': 6,
            'surrender': 7  
        }
        
        if panel_name in panel_map:
            self.stacked_panels.setCurrentIndex(panel_map[panel_name])
    
    def logout(self):
        reply = QMessageBox.question(self, 'Confirm Logout', 
                                   'Are you sure you want to logout?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_signal.emit()
