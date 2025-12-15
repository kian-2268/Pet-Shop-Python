import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFontDatabase, QIcon
from ui.login_window import LoginWindow
from ui.admin_dashboard import AdminDashboard
from ui.staff_dashboard import StaffDashboard
from ui.customer_dashboard import CustomerDashboard
from database.db_connection import DatabaseConnection
from ui.panels.sales_panel import SalesPanel
from ui.panels.adoption_panel import AdoptionPanel
from ui.panels.profile_panel import ProfilePanel
from ui.panels.order_history_panel import OrderHistoryPanel
from ui.panels.surrender_panel import SurrenderPanel
import mysql.connector
from mysql.connector import Error

class MainWindow(QMainWindow):
    cart_updated = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cuddle Corner")
        self.showMaximized()
        
        # Initialize database
        self.db = DatabaseConnection()
        
        # Create stacked widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create windows
        self.login_window = LoginWindow(self.db)
        self.admin_dashboard = None
        self.staff_dashboard = None
        self.customer_dashboard = None
        
        # Add login window
        self.stacked_widget.addWidget(self.login_window)
        
        # Connect signals
        self.login_window.login_successful.connect(self.handle_login_success)
        self.login_window.register_requested.connect(self.show_register)
    
    def handle_login_success(self, user_data):
        user_id, username, role = user_data
        
        # Remove current dashboard
        if self.stacked_widget.count() > 1:
            old_widget = self.stacked_widget.widget(1)
            self.stacked_widget.removeWidget(old_widget)
            old_widget.deleteLater()
        
        # Create appropriate dashboard
        if role == 'admin':
            self.admin_dashboard = AdminDashboard(self.db, user_id, username.capitalize())
            self.admin_dashboard.logout_signal.connect(self.show_login)
            self.stacked_widget.addWidget(self.admin_dashboard)
        elif role == 'staff':
            self.staff_dashboard = StaffDashboard(self.db, user_id, username.capitalize())
            self.staff_dashboard.logout_signal.connect(self.show_login)
            self.stacked_widget.addWidget(self.staff_dashboard)
        else:  # customer
            self.customer_dashboard = CustomerDashboard(self.db, user_id, username.capitalize())
            self.customer_dashboard.logout_signal.connect(self.show_login)
            self.stacked_widget.addWidget(self.customer_dashboard)
        
        self.stacked_widget.setCurrentIndex(1)
    
    def show_login(self):
        # Clear any existing dashboards
        while self.stacked_widget.count() > 1:
            widget = self.stacked_widget.widget(1)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        
        self.stacked_widget.setCurrentIndex(0)
        self.login_window.clear_fields()
    
    def show_register(self):
        # Implementation for registration dialog
        from ui.register_dialog import RegisterDialog
        dialog = RegisterDialog(self.db, self)
        dialog.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.showMaximized() 
    window.show()
    
    sys.exit(app.exec())
