from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QHeaderView, QFrame, 
                             QScrollArea)
from PyQt6.QtCore import QDateTime, Qt
from datetime import datetime
from models.order_model import OrderModel
from models.appointment_model import AppointmentModel
from models.pet_model import PetModel
from models.product_model import ProductModel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class ReportsPanel(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.order_model = OrderModel(db)
        self.appointment_model = AppointmentModel(db)
        self.pet_model = PetModel(db)
        self.product_model = ProductModel(db)
        self.init_ui()
        self.load_sales_report()  # Start with sales report by default
    
    def init_ui(self):
        self.setStyleSheet("background-color: #f9d162;")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        
        # Header 
        header_layout = QHBoxLayout()
        title = QLabel("Reports & Analytics")
        title.setStyleSheet("background-color: #f9fafb; font-size: 25px; font-weight: bold; color: black;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(10)
        
        # Filters 
        self.filter_layout = QHBoxLayout()
        
        # Filter labels with white background 
        report_label = QLabel("Report Type:")
        report_label.setStyleSheet("""
            QLabel {    
                background-color: #f9fafb;
                color: black;
                padding: 5px 10px;
            }
        """)
        self.filter_layout.addWidget(report_label)
        
        self.report_combo = QComboBox()
        self.report_combo.addItems([
            "Sales Summary", 
            "Appointment Analytics", 
            "Inventory Status",
            "Pet Adoption Stats"
        ])
        self.report_combo.setStyleSheet("""
            QComboBox {
                color: black;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #555;
            }
        """)
        self.report_combo.currentTextChanged.connect(self.on_report_type_changed)
        self.filter_layout.addWidget(self.report_combo)
        
        # Date filter labels 
        date_from_label = QLabel("Date From:")
        date_from_label.setStyleSheet("""
            QLabel {    
                background-color: #f9fafb;
                color: black;
                padding: 5px 10px;
                margin-left: 10px;
            }
        """)
        self.filter_layout.addWidget(date_from_label)
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDateTime.currentDateTime().date().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("""
            QDateEdit {
                color: black;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        self.filter_layout.addWidget(self.start_date)
        
        date_to_label = QLabel("To:")
        date_to_label.setStyleSheet("""
            QLabel {    
                background-color: #f9fafb;
                color: black;
                padding: 5px 10px;
            }
        """)
        self.filter_layout.addWidget(date_to_label)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDateTime.currentDateTime().date())
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("""
            QDateEdit {
                color: black;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        self.filter_layout.addWidget(self.end_date)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_report)
        self.filter_layout.addWidget(self.refresh_btn)
        
        self.filter_layout.addStretch()
        main_layout.addLayout(self.filter_layout)
        main_layout.addSpacing(20)
        
        # Create a scroll area for the report content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
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
        
        # Create container for report content
        self.report_container = QWidget()
        self.report_container.setStyleSheet("background-color: transparent;")
        self.report_layout = QVBoxLayout()
        self.report_layout.setContentsMargins(0, 0, 0, 0)
        self.report_layout.setSpacing(20)
        self.report_container.setLayout(self.report_layout)
        
        self.scroll_area.setWidget(self.report_container)
        main_layout.addWidget(self.scroll_area)
        
        self.setLayout(main_layout)
    
    def on_report_type_changed(self, report_type):
        # Handle report type change
        if report_type == "Sales Summary":
            self.load_sales_report()
        elif report_type == "Appointment Analytics":
            self.load_appointment_report()
        elif report_type == "Inventory Status":
            self.load_inventory_report()
        elif report_type == "Pet Adoption Stats":
            self.load_pet_report()
    
    def refresh_report(self):
        # Refresh current report
        report_type = self.report_combo.currentText()
        self.on_report_type_changed(report_type)
    
    def load_sales_report(self):
        # Load sales report - WITHOUT Recent Orders table
        self.clear_report_content()
        
        start_date = self.start_date.date().toString('yyyy-MM-dd')
        end_date = self.end_date.date().toString('yyyy-MM-dd')
        
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
        
        # Report title
        report_title = QLabel("Sales Summary")
        report_title.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                font-size: 20px;
                font-weight: bold;
                color: black;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        self.report_layout.addWidget(report_title)
        
        # Stats cards container
        stats_container = QWidget()
        stats_container.setStyleSheet("background-color: transparent;")
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(15)
        
        # Create stats cards
        self.create_stat_card("Total Revenue", f"₱{total_revenue:,.2f}", "#f9fafb", "#27ae60", stats_layout)
        self.create_stat_card("Total Orders", str(total_orders), "#f9fafb", "#3498db", stats_layout)
        self.create_stat_card("Avg Order Value", f"₱{avg_order_value:.2f}", "#f9fafb", "#e74c3c", stats_layout)
        self.create_stat_card("Date Range", f"{start_date} to {end_date}", "#f9fafb", "#f39c12", stats_layout)
        
        stats_container.setLayout(stats_layout)
        self.report_layout.addWidget(stats_container)
        
        # Show sales chart
        self.create_sales_chart(filtered_orders)
        
        # NO Recent Orders table - Removed as requested
        
        if not filtered_orders:
            no_data_label = QLabel("No sales data found for the selected period")
            no_data_label.setStyleSheet("""
                QLabel {
                    background-color: #f9fafb;
                    color: #7f8c8d;
                    font-size: 16px;
                    padding: 20px;
                    border-radius: 5px;
                    text-align: center;
                }
            """)
            self.report_layout.addWidget(no_data_label)
        
        # Add stretch at the end
        self.report_layout.addStretch()
    
    def load_appointment_report(self):
        # Load appointment report
        self.clear_report_content()
        
        start_date = self.start_date.date().toString('yyyy-MM-dd')
        end_date = self.end_date.date().toString('yyyy-MM-dd')
        
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
        
        # Report title
        report_title = QLabel("Appointment Analytics")
        report_title.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                font-size: 20px;
                font-weight: bold;
                color: black;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        self.report_layout.addWidget(report_title)
        
        # Stats cards container
        stats_container = QWidget()
        stats_container.setStyleSheet("background-color: transparent;")
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(15)
        
        # Create stats cards
        self.create_stat_card("Total Appointments", str(total_appointments), "#f9fafb", "#3498db", stats_layout)
        self.create_stat_card("Completed", str(status_count['Completed']), "#f9fafb", "#27ae60", stats_layout)
        self.create_stat_card("Pending", str(status_count['Pending']), "#f9fafb", "#f39c12", stats_layout)
        self.create_stat_card("Cancelled", str(status_count['Cancelled']), "#f9fafb", "#e74c3c", stats_layout)
        
        stats_container.setLayout(stats_layout)
        self.report_layout.addWidget(stats_container)
        
        # Appointment chart
        if total_appointments > 0:
            self.create_appointment_chart(status_count, service_count)
        else:
            no_data_label = QLabel("No appointment data found for the selected period")
            no_data_label.setStyleSheet("""
                QLabel {
                    background-color: #f9fafb;
                    color: #7f8c8d;
                    font-size: 16px;
                    padding: 20px;
                    border-radius: 5px;
                    text-align: center;
                }
            """)
            self.report_layout.addWidget(no_data_label)
        
        # Add stretch at the end
        self.report_layout.addStretch()
    
    def load_inventory_report(self):
        """Load inventory report"""
        self.clear_report_content()
        
        products = self.product_model.get_all_products()
        
        # Calculate inventory stats
        total_products = len(products)
        out_of_stock = sum(1 for p in products if p['quantity'] == 0)
        low_stock = sum(1 for p in products if 0 < p['quantity'] <= p['reorder_level'])
        total_value = sum(float(p['price']) * p['quantity'] for p in products)
        
        # Report title
        report_title = QLabel("Inventory Status")
        report_title.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                font-size: 20px;
                font-weight: bold;
                color: black;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        self.report_layout.addWidget(report_title)
        
        # Stats cards container
        stats_container = QWidget()
        stats_container.setStyleSheet("background-color: transparent;")
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(15)
        
        # Create stats cards
        self.create_stat_card("Total Products", str(total_products), "#f9fafb", "#3498db", stats_layout)
        self.create_stat_card("Out of Stock", str(out_of_stock), "#f9fafb", "#e74c3c", stats_layout)
        self.create_stat_card("Low Stock", str(low_stock), "#f9fafb", "#f39c12", stats_layout)
        self.create_stat_card("Inventory Value", f"₱{total_value:,.2f}", "#f9fafb", "#27ae60", stats_layout)
        
        stats_container.setLayout(stats_layout)
        self.report_layout.addWidget(stats_container)
        
        # Low stock products table
        low_stock_products = [p for p in products if p['quantity'] <= p['reorder_level']]
        if low_stock_products:
            self.create_inventory_table(low_stock_products)
        else:
            good_stock_label = QLabel("All products have sufficient stock levels")
            good_stock_label.setStyleSheet("""
                QLabel {
                    background-color: #f9fafb;
                    color: #27ae60;
                    font-size: 16px;
                    padding: 20px;
                    border-radius: 5px;
                    text-align: center;
                    font-weight: bold;
                }
            """)
            self.report_layout.addWidget(good_stock_label)
        
        # Add stretch at the end
        self.report_layout.addStretch()
    
    def load_pet_report(self):
        """Load pet report"""
        self.clear_report_content()
        
        start_date = self.start_date.date().toString('yyyy-MM-dd')
        end_date = self.end_date.date().toString('yyyy-MM-dd')
        
        pets = self.pet_model.get_all_pets()
        
        # Count pets by status and species
        status_count = {'Available': 0, 'Sold': 0, 'Adopted': 0, 'Reserved': 0}
        species_count = {}
        
        for pet in pets:
            status_count[pet['status']] += 1
            species_count[pet['species']] = species_count.get(pet['species'], 0) + 1
        
        total_pets = len(pets)
        available_pets = status_count['Available']
        
        # Report title
        report_title = QLabel("Pet Adoption Stats")
        report_title.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                font-size: 20px;
                font-weight: bold;
                color: black;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        self.report_layout.addWidget(report_title)
        
        # Stats cards container
        stats_container = QWidget()
        stats_container.setStyleSheet("background-color: transparent;")
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(15)
        
        # Create stats cards
        self.create_stat_card("Total Pets", str(total_pets), "#f9fafb", "#3498db", stats_layout)
        self.create_stat_card("Available", str(available_pets), "#f9fafb", "#27ae60", stats_layout)
        self.create_stat_card("Sold/Adopted", str(status_count['Sold'] + status_count['Adopted']), "#f9fafb", "#e74c3c", stats_layout)
        self.create_stat_card("Species", str(len(species_count)), "#f9fafb", "#f39c12", stats_layout)
        
        stats_container.setLayout(stats_layout)
        self.report_layout.addWidget(stats_container)
        
        # Pets chart
        if total_pets > 0:
            self.create_pets_chart(status_count, species_count)
        else:
            no_data_label = QLabel("No pet data available")
            no_data_label.setStyleSheet("""
                QLabel {
                    background-color: #f9fafb;
                    color: #7f8c8d;
                    font-size: 16px;
                    padding: 20px;
                    border-radius: 5px;
                    text-align: center;
                }
            """)
            self.report_layout.addWidget(no_data_label)
        
        # Add stretch at the end
        self.report_layout.addStretch()
    
    def clear_report_content(self):
        """Clear only the report content, not the headers/filters"""
        while self.report_layout.count():
            child = self.report_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def create_stat_card(self, title, value, bg_color, text_color, layout):
        """Create a stat card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 5px;
                padding: 10px 15px;
            }}
        """)
        
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: #7f8c8d;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 20px;
                font-weight: bold;
            }}
        """)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        card.setLayout(card_layout)
        
        layout.addWidget(card)
    
    def create_sales_chart(self, orders):
        # Group orders by date
        daily_sales = {}
        for order in orders:
            order_date = order['order_date']
            if isinstance(order_date, str):
                order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            date_str = order_date.strftime('%Y-%m-%d')
            daily_sales[date_str] = daily_sales.get(date_str, 0) + float(order['total_amount'])
        
        # Create matplotlib figure with smaller fonts
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#f9d162')
        
        # Set smaller font sizes for chart
        plt.rcParams.update({
            'font.size': 9,
            'axes.titlesize': 10,
            'axes.labelsize': 9,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8
        })
        
        if daily_sales:
            dates = list(daily_sales.keys())
            amounts = list(daily_sales.values())
            
            ax.bar(dates, amounts, color='#3498db', alpha=0.7)
            ax.set_title('Daily Sales Revenue', fontweight='bold')
            ax.set_ylabel('Revenue (₱)', fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
            ax.set_facecolor('#f9fafb')
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₱{x:,.0f}'))
            
            for spine in ax.spines.values():
                spine.set_edgecolor('#ddd')
        else:
            ax.text(0.5, 0.5, 'No sales data for selected period', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=10)
            ax.set_facecolor('#f9fafb')
        
        fig.tight_layout()
        
        # Embed in PyQt
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: #f9fafb; border-radius: 8px; padding: 10px;")
        self.report_layout.addWidget(canvas)
        
        # Reset font sizes
        plt.rcParams.update(plt.rcParamsDefault)
    
    def create_appointment_chart(self, status_count, service_count):
        # Set smaller font sizes for chart
        plt.rcParams.update({
            'font.size': 9,
            'axes.titlesize': 10,
            'axes.labelsize': 9,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8
        })
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        fig.patch.set_facecolor('#f9d162')
        
        # Status pie chart
        labels = [k for k, v in status_count.items() if v > 0]
        sizes = [v for v in status_count.values() if v > 0]
        colors = ['#f39c12', '#3498db', '#27ae60', '#e74c3c']
        
        ax1.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct='%1.1f%%', startangle=90)
        ax1.set_title('Appointment Status', fontweight='bold')
        ax1.set_facecolor('#f9fafb')
        
        # Service type bar chart
        if service_count:
            services = list(service_count.keys())
            counts = list(service_count.values())
            
            ax2.bar(services, counts, color='#3498db', alpha=0.7)
            ax2.set_title('Appointments by Service Type', fontweight='bold')
            ax2.tick_params(axis='x', rotation=45)
            ax2.set_facecolor('#f9fafb')
            
            for spine in ax2.spines.values():
                spine.set_edgecolor('#ddd')
        else:
            ax2.text(0.5, 0.5, 'No service data', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=10)
            ax2.set_facecolor('#f9fafb')
        
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: #f9fafb; border-radius: 8px; padding: 10px;")
        self.report_layout.addWidget(canvas)
        
        # Reset font sizes
        plt.rcParams.update(plt.rcParamsDefault)
    
    def create_inventory_table(self, products):
        table_header = QLabel("Low Stock Products")
        table_header.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                font-size: 18px;
                font-weight: bold;
                color: black;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        self.report_layout.addWidget(table_header)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Product", "Category", "Current Stock", "Reorder Level", "Status"])
        
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e1e1e1;
                border-radius: 8px;
                background: white;
                color: black;
                margin-top: 5px;
            }
            QHeaderView::section {
                background: #f8f9fa;
                padding: 10px;
                border: none;
                font-weight: bold;
                color: black;
            }
        """)
        
        table.setRowCount(len(products))
        for row, product in enumerate(products):
            table.setItem(row, 0, QTableWidgetItem(product['name']))
            table.setItem(row, 1, QTableWidgetItem(product['category']))
            table.setItem(row, 2, QTableWidgetItem(str(product['quantity'])))
            table.setItem(row, 3, QTableWidgetItem(str(product['reorder_level'])))
            
            # Status with colors like SurrenderPanel
            status = "Out of Stock" if product['quantity'] == 0 else "Low Stock"
            status_item = QTableWidgetItem(status)
            if product['quantity'] == 0:
                status_item.setForeground(Qt.GlobalColor.darkRed)
            else:
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            table.setItem(row, 4, status_item)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_layout.addWidget(table)
    
    def create_pets_chart(self, status_count, species_count):
        # Set smaller font sizes for chart
        plt.rcParams.update({
            'font.size': 9,
            'axes.titlesize': 10,
            'axes.labelsize': 9,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8
        })
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        fig.patch.set_facecolor('#f9d162')
        
        # Status bar chart
        statuses = [k for k, v in status_count.items() if v > 0]
        counts = [v for v in status_count.values() if v > 0]
        
        colors = ['#27ae60', '#e74c3c', '#3498db', '#f39c12']
        ax1.bar(statuses, counts, color=colors[:len(statuses)], alpha=0.7)
        ax1.set_title('Pets by Status', fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_facecolor('#f9fafb')
        
        for spine in ax1.spines.values():
            spine.set_edgecolor('#ddd')
        
        # Species pie chart
        if species_count:
            species = list(species_count.keys())
            species_counts = list(species_count.values())
            
            ax2.pie(species_counts, labels=species, autopct='%1.1f%%', startangle=90)
            ax2.set_title('Pets by Species', fontweight='bold')
            ax2.set_facecolor('#f9fafb')
        else:
            ax2.text(0.5, 0.5, 'No species data', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=10)
            ax2.set_facecolor('#f9fafb')
        
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: #f9fafb; border-radius: 8px; padding: 10px;")
        self.report_layout.addWidget(canvas)
        
        # Reset font sizes
        plt.rcParams.update(plt.rcParamsDefault)
