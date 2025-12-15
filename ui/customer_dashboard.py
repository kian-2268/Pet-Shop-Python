from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedWidget, QFrame,
                             QMessageBox)
import os
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QIcon
from ui.panels.customer_pets_panel import CustomerPetsPanel
from ui.panels.customer_products_panel import CustomerProductsPanel
from ui.panels.cart_panel import CartPanel
from ui.panels.customer_appointments_panel import CustomerAppointmentsPanel
from ui.panels.adoption_request_panel import AdoptionRequestPanel
from ui.panels.profile_panel import ProfilePanel
from ui.panels.order_history_panel import OrderHistoryPanel
from ui.panels.surrender_panel import SurrenderPanel

class CustomerDashboard(QMainWindow):
    logout_signal = pyqtSignal()
    
    def __init__(self, db, user_id, username):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.username = username
        self.init_ui()
        self.showFullScreen()
    
    def init_ui(self):
        self.setWindowTitle("Customer Dashboard - Pet Shop Management System")
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
        
        # Set background image
        self.set_sidebar_background(sidebar)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)

        # Top bar with welcome message only
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
            # Try to load an icon
            pixmap = QPixmap("system_images/p1.png")
            if pixmap.isNull():
                # Try alternative
                pixmap = QPixmap("🙋🏼‍♀️")
    
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
        
        # Navigation buttons
        nav_buttons = [
            (" Browse Pets", "pets", "system_images/pets.png"),
            (" Products", "products", "system_images/products.png"),
            (" My Cart", "cart", "system_images/cart.png"),
            (" Adoption", "adoption", "system_images/adopt.png"),
            (" Surrender Pet", "surrender", "system_images/surrender.png"),
            (" Appointments", "appointments", "system_images/appointment.png"),
            (" Order History", "order_history", "system_images/order-history.png"),
            (" My Profile", "profile", "system_images/user.png")
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
                        'pets': '🐾',
                        'products': '📦',
                        'cart': '🛒',
                        'adoption': '🏠',
                        'surrender': '💔',
                        'appointments': '📅',
                        'order_history': '📋',
                        'profile': '👤'
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
        
        # Set icon using QIcon
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
    
    def set_sidebar_background(self, sidebar):
        try:
            # Load the image
            pixmap = QPixmap("system_images/side.png")
            
            if pixmap.isNull():
                print("Background image not found or failed to load")
                # Fallback
                sidebar.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #8e44ad, stop:0.5 #9b59b6, stop:1 #3498db);
                        border: none;
                    }
                """)
                return
            
            scaled_pixmap = pixmap.scaledToWidth(250, Qt.TransformationMode.SmoothTransformation)
            
            print(f"Background image scaled to: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
            
            palette = QPalette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled_pixmap))
            sidebar.setPalette(palette)
            sidebar.setAutoFillBackground(True)
            
        except Exception as e:
            print(f"Error setting background: {e}")
            # Fallback
            sidebar.setStyleSheet("background: #8e44ad;")
    
    def create_main_content(self, main_layout):
        self.stacked_panels = QStackedWidget()
        self.stacked_panels.setStyleSheet("""
            QStackedWidget {
                background: #f8f9fa;
                border: none;
            }
        """)
        
        self.pets_panel = CustomerPetsPanel(self.db, self.user_id)
        self.products_panel = CustomerProductsPanel(self.db, self.user_id)
        self.cart_panel = CartPanel(self.db, self.user_id)
        self.adoption_panel = AdoptionRequestPanel(self.db, self.user_id)
        self.surrender_panel = SurrenderPanel(self.db, self.user_id)
        self.appointments_panel = CustomerAppointmentsPanel(self.db, self.user_id)
        self.order_history_panel = OrderHistoryPanel(self.db, self.user_id)
        self.profile_panel = ProfilePanel(self.db, self.user_id)
        
        self.stacked_panels.addWidget(self.pets_panel)
        self.stacked_panels.addWidget(self.products_panel)
        self.stacked_panels.addWidget(self.cart_panel)
        self.stacked_panels.addWidget(self.adoption_panel)
        self.stacked_panels.addWidget(self.surrender_panel)
        self.stacked_panels.addWidget(self.appointments_panel)
        self.stacked_panels.addWidget(self.order_history_panel)
        self.stacked_panels.addWidget(self.profile_panel)
        
        main_layout.addWidget(self.stacked_panels, 1)
    
    def switch_panel(self):
        button = self.sender()
        panel_name = button.property('panel')
        
        for btn in self.nav_buttons_group:
            btn.setChecked(False)
        
        button.setChecked(True)
        
        panel_map = {
            'pets': 0,
            'products': 1,
            'cart': 2,
            'adoption': 3,
            'surrender': 4,
            'appointments': 5,
            'order_history': 6,
            'profile': 7
        }
        
        if panel_name in panel_map:
            self.stacked_panels.setCurrentIndex(panel_map[panel_name])
    
    def logout(self):
        reply = QMessageBox.question(self, 'Confirm Logout', 
                                   'Are you sure you want to logout?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_signal.emit()
