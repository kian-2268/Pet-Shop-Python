from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QMessageBox, QHeaderView,
                             QGroupBox, QFrame)
from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
from models.order_model import OrderModel
from models.appointment_model import AppointmentModel
from models.pet_model import PetModel
from models.product_model import ProductModel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class ReportsPanel(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.order_model = OrderModel(db)
        self.appointment_model = AppointmentModel(db)
        self.pet_model = PetModel(db)
        self.product_model = ProductModel(db)
        self.init_ui()
        self.load_reports()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Reports & Analytics")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Filters
        filters_layout = QHBoxLayout()
        
        filters_layout.addWidget(QLabel("Report Type:"))
        self.report_combo = QComboBox()
        self.report_combo.addItems([
            "Sales Summary", 
            "Appointment Analytics", 
            "Inventory Status",
            "Pet Adoption Stats"
        ])
        self.report_combo.currentTextChanged.connect(self.load_reports)
        
        filters_layout.addWidget(self.report_combo)
        
        filters_layout.addWidget(QLabel("Date Range:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDateTime.currentDateTime().date().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDateTime.currentDateTime().date())
        self.end_date.setCalendarPopup(True)
        
        filters_layout.addWidget(self.start_date)
        filters_layout.addWidget(QLabel("to"))
        filters_layout.addWidget(self.end_date)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.load_reports)
        
        filters_layout.addWidget(refresh_btn)
        filters_layout.addStretch()
        
        layout.addLayout(filters_layout)
        layout.addSpacing(20)
        
        # Stats cards
        self.stats_layout = QHBoxLayout()
        layout.addLayout(self.stats_layout)
        
        # Charts and tables area
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
        
        self.setLayout(layout)
    
    def load_reports(self):
        # Clear previous content
        self.clear_layout(self.stats_layout)
        self.clear_layout(self.content_layout)
        
        report_type = self.report_combo.currentText()
        start_date = self.start_date.date().toString('yyyy-MM-dd')
        end_date = self.end_date.date().toString('yyyy-MM-dd')
        
        if report_type == "Sales Summary":
            self.show_sales_report(start_date, end_date)
        elif report_type == "Appointment Analytics":
            self.show_appointment_report(start_date, end_date)
        elif report_type == "Inventory Status":
            self.show_inventory_report()
        elif report_type == "Pet Adoption Stats":
            self.show_pet_report(start_date, end_date)
    
    def show_sales_report(self, start_date, end_date):
        # Get sales data
        orders = self.order_model.get_all_orders()
        
        # Filter orders by date
        filtered_orders = []
        total_revenue = 0
        total_orders = 0
        
        for order in orders:
            order_date = order['order_date']
            if isinstance(order_date, str):
                order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            
            if start_date <= order_date.strftime('%Y-%m-%d') <= end_date:
                filtered_orders.append(order)
                total_revenue += float(order['total_amount'])
                total_orders += 1
        
        # Calculate average order value
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Show stats cards
        self.create_stat_card("Total Revenue", f"${total_revenue:,.2f}", "#27ae60")
        self.create_stat_card("Total Orders", str(total_orders), "#3498db")
        self.create_stat_card("Avg Order Value", f"${avg_order_value:.2f}", "#e74c3c")
        self.create_stat_card("Date Range", f"{start_date} to {end_date}", "#f39c12")
        
        # Show sales chart
        self.create_sales_chart(filtered_orders)
        
        # Show recent orders table
        self.create_orders_table(filtered_orders[:10])  # Show last 10 orders
    
    def show_appointment_report(self, start_date, end_date):
        appointments = self.appointment_model.get_all_appointments()
        
        # Filter and count by status
        status_count = {'Pending': 0, 'Approved': 0, 'Completed': 0, 'Cancelled': 0}
        service_count = {}
        
        for apt in appointments:
            apt_date = apt['appointment_date']
            if isinstance(apt_date, str):
                apt_date = datetime.strptime(apt_date, '%Y-%m-%d %H:%M:%S')
            
            if start_date <= apt_date.strftime('%Y-%m-%d') <= end_date:
                status_count[apt['status']] += 1
                service_count[apt['service_type']] = service_count.get(apt['service_type'], 0) + 1
        
        total_appointments = sum(status_count.values())
        
        # Stats cards
        self.create_stat_card("Total Appointments", str(total_appointments), "#3498db")
        self.create_stat_card("Completed", str(status_count['Completed']), "#27ae60")
        self.create_stat_card("Pending", str(status_count['Pending']), "#f39c12")
        self.create_stat_card("Cancelled", str(status_count['Cancelled']), "#e74c3c")
        
        # Appointment chart
        self.create_appointment_chart(status_count, service_count)
    
    def show_inventory_report(self):
        products = self.product_model.get_all_products()
        
        # Calculate inventory stats
        total_products = len(products)
        out_of_stock = sum(1 for p in products if p['quantity'] == 0)
        low_stock = sum(1 for p in products if 0 < p['quantity'] <= p['reorder_level'])
        total_value = sum(float(p['price']) * p['quantity'] for p in products)
        
        # Stats cards
        self.create_stat_card("Total Products", str(total_products), "#3498db")
        self.create_stat_card("Out of Stock", str(out_of_stock), "#e74c3c")
        self.create_stat_card("Low Stock", str(low_stock), "#f39c12")
        self.create_stat_card("Inventory Value", f"${total_value:,.2f}", "#27ae60")
        
        # Low stock products table
        low_stock_products = [p for p in products if p['quantity'] <= p['reorder_level']]
        self.create_inventory_table(low_stock_products)
    
    def show_pet_report(self, start_date, end_date):
        pets = self.pet_model.get_all_pets()
        
        # Count pets by status and species
        status_count = {'Available': 0, 'Sold': 0, 'Adopted': 0, 'Reserved': 0}
        species_count = {}
        
        for pet in pets:
            status_count[pet['status']] += 1
            species_count[pet['species']] = species_count.get(pet['species'], 0) + 1
        
        total_pets = len(pets)
        available_pets = status_count['Available']
        
        # Stats cards
        self.create_stat_card("Total Pets", str(total_pets), "#3498db")
        self.create_stat_card("Available", str(available_pets), "#27ae60")
        self.create_stat_card("Sold/Adopted", str(status_count['Sold'] + status_count['Adopted']), "#e74c3c")
        self.create_stat_card("Species", str(len(species_count)), "#f39c12")
        
        # Pets chart
        self.create_pets_chart(status_count, species_count)
    
    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setFixedSize(200, 100)
        card.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        
        self.stats_layout.addWidget(card)
    
    def create_sales_chart(self, orders):
        # Group orders by date
        daily_sales = {}
        for order in orders:
            order_date = order['order_date']
            if isinstance(order_date, str):
                order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            date_str = order_date.strftime('%Y-%m-%d')
            daily_sales[date_str] = daily_sales.get(date_str, 0) + float(order['total_amount'])
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 4))
        
        if daily_sales:
            dates = list(daily_sales.keys())
            amounts = list(daily_sales.values())
            
            ax.bar(dates, amounts, color='#3498db', alpha=0.7)
            ax.set_title('Daily Sales Revenue')
            ax.set_ylabel('Revenue ($)')
            ax.tick_params(axis='x', rotation=45)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        else:
            ax.text(0.5, 0.5, 'No sales data for selected period', 
                   ha='center', va='center', transform=ax.transAxes)
        
        fig.tight_layout()
        
        # Embed in PyQt
        canvas = FigureCanvas(fig)
        self.content_layout.addWidget(canvas)
    
    def create_orders_table(self, orders):
        table_group = QGroupBox("Recent Orders")
        layout = QVBoxLayout()
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Order ID", "Customer", "Date", "Amount", "Status"])
        
        table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            table.setItem(row, 0, QTableWidgetItem(str(order['id'])))
            table.setItem(row, 1, QTableWidgetItem(order.get('customer_name', 'N/A')))
            
            order_date = order['order_date']
            if isinstance(order_date, str):
                order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            table.setItem(row, 2, QTableWidgetItem(order_date.strftime('%Y-%m-%d')))
            
            table.setItem(row, 3, QTableWidgetItem(f"${float(order['total_amount']):.2f}"))
            table.setItem(row, 4, QTableWidgetItem(order['status']))
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)
        table_group.setLayout(layout)
        self.content_layout.addWidget(table_group)
    
    def create_appointment_chart(self, status_count, service_count):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Status pie chart
        labels = [k for k, v in status_count.items() if v > 0]
        sizes = [v for v in status_count.values() if v > 0]
        colors = ['#f39c12', '#3498db', '#27ae60', '#e74c3c']
        
        ax1.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct='%1.1f%%')
        ax1.set_title('Appointment Status')
        
        # Service type bar chart
        if service_count:
            services = list(service_count.keys())
            counts = list(service_count.values())
            
            ax2.bar(services, counts, color='#3498db', alpha=0.7)
            ax2.set_title('Appointments by Service Type')
            ax2.tick_params(axis='x', rotation=45)
        else:
            ax2.text(0.5, 0.5, 'No appointment data', 
                    ha='center', va='center', transform=ax2.transAxes)
        
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        self.content_layout.addWidget(canvas)
    
    def create_inventory_table(self, products):
        table_group = QGroupBox("Low Stock Products")
        layout = QVBoxLayout()
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Product", "Category", "Current Stock", "Reorder Level", "Status"])
        
        table.setRowCount(len(products))
        for row, product in enumerate(products):
            table.setItem(row, 0, QTableWidgetItem(product['name']))
            table.setItem(row, 1, QTableWidgetItem(product['category']))
            table.setItem(row, 2, QTableWidgetItem(str(product['quantity'])))
            table.setItem(row, 3, QTableWidgetItem(str(product['reorder_level'])))
            
            status = "Out of Stock" if product['quantity'] == 0 else "Low Stock"
            status_item = QTableWidgetItem(status)
            if product['quantity'] == 0:
                status_item.setBackground(Qt.GlobalColor.red)
                status_item.setForeground(Qt.GlobalColor.white)
            else:
                status_item.setBackground(Qt.GlobalColor.yellow)
            table.setItem(row, 4, status_item)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)
        table_group.setLayout(layout)
        self.content_layout.addWidget(table_group)
    
    def create_pets_chart(self, status_count, species_count):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Status bar chart
        statuses = [k for k, v in status_count.items() if v > 0]
        counts = [v for v in status_count.values() if v > 0]
        
        colors = ['#27ae60', '#e74c3c', '#3498db', '#f39c12']
        ax1.bar(statuses, counts, color=colors[:len(statuses)], alpha=0.7)
        ax1.set_title('Pets by Status')
        ax1.tick_params(axis='x', rotation=45)
        
        # Species pie chart
        if species_count:
            species = list(species_count.keys())
            species_counts = list(species_count.values())
            
            ax2.pie(species_counts, labels=species, autopct='%1.1f%%')
            ax2.set_title('Pets by Species')
        else:
            ax2.text(0.5, 0.5, 'No pet data', 
                    ha='center', va='center', transform=ax2.transAxes)
        
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        self.content_layout.addWidget(canvas)
    
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()