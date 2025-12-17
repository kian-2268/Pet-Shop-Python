# 🐾 Cuddle Corner Pet Shop Management System

A comprehensive desktop application for managing all aspects of a modern pet shop, built with Python and PyQt6. The system handles pet adoption, product sales, customer appointments, and administrative functions with role-based access control.

---

## 👥 Team Members and Roles
| Name | Role |
|------|------|
| Khiana Marie T. Enoc | Frontend / UI Designer / Backend / Database / System Architecture |
| Jude Emmanuel Corage | Testing / Documentation |

---

## 🧭 Project Overview
Cuddle Corner Pet Shop Management System allows users to:

- Manage pet inventory with complete CRUD operations and image upload
- Process customer orders with integrated shopping cart and checkout
- Handle pet adoption and surrender requests
- Book and manage pet service appointments
- Track order history with status updates
- Manage user profiles with secure authentication

All data (pets, products, orders, users) is stored in MySQL database.

---

## 🧩 Features
- **User Authentication System** - Secure login with role-based access (Admin/Staff/Customer)
- **Pet Management** - Add, edit, delete pets with detailed information and images
- **Product Catalog** - Browse products with search, filtering, and shopping cart functionality
- **Order Processing** - Complete e-commerce flow with receipt printing
- **Appointment Scheduling** - Book pet services with availability checking
- **Adoption System** - Manage adoption requests with status tracking
- **Surrender Portal** - Handle pet surrender requests from customers
- **Profile Management** - Update personal information and change passwords
- **Responsive UI** - Modern PyQt6 interface with consistent styling

---

## ⚙️ How to Run the Project
1. Clone the repository: https://github.com/kian-2268/Pet-Shop-Python.git
2. Install Python 3.8+ and required dependencies:
   ```bash
   pip install PyQt6 mysql-connector-python
   ```
3. Configure database connection in the application
4. Run the application:
   ```bash
   python main.py
   ```

**Application Flow:**
1. Launch the system and login with appropriate credentials
2. Admin/Staff can manage pets, products, and view orders
3. Customers can browse pets/products, add to cart, and checkout
4. Customers can submit adoption/surrender requests
5. Customers can book appointments for pet services
6. Customers can update their profile information

---

## 🗂️ Project Structure
```
Pet-Shop-Python/
├── database/
│   ├── __init__.py                        # Make this a package
│   └── db_connection.py                   # database connection
├── ui/                                    # PyQt6 UI components
│   ├── __init__.py                        # Make this a package
│   ├── login_window.py                    # Login interface with authentication
│   ├── admin_dashboard.py                 # Admin dashboard
│   ├── customer_dashboard.py              # Customer dashboard
│   ├── forgot_password_dialog.py          # Reset password
│   ├── register_dialog.py                 # Register users
│   ├── staff_dashboard.py                 # Staff dashboard
│   └── panels/                            # All users' panel
│       ├── __init__.py                    # Make this a package
│       ├── pet_management_panel.py        # Pet CRUD operations
│       ├── customer_products_panel.py     # Product browsing and cart
│       ├── cart_panel.py                  # Shopping cart and checkout
│       ├── adoption_panel.py              # Admin-facing adoption panel
│       ├── adoption_request_panel.py      # Adoption request management
│       ├── surrender_panel.py             # Pet surrender request handling
│       ├── appointment_panel.py           # Admin-facing appointment panel
│       ├── attendance_panel.py            # Attendance management
│       ├── customer_appointments_panel.py # Appointment booking
│       ├── pos_panel.py                   # POS system
│       ├── staff_management_panel.py      # Staff management
│       ├── reports_panel.py               # Sales reports, appointment, and inventory
│       ├── sales_panel.py                 # Sales management
│       ├── inventory_panel.py             # Inventory management
│       ├── customer_pets_panel.py         # Pet browsing and adoption
│       ├── surrender_management_panel.py  # Manage all surrender request
│       ├── customer_management_panel.py   # Customer management
│       ├── order_history_panel.py         # Order tracking and history
│       └── profile_panel.py               # User profile management
├── models/                                # Database models
│   ├── __init__.py                        # Make this a package
│   ├── user_model.py                      # User authentication and management
│   ├── pet_model.py                       # Pet data operations
│   ├── product_model.py                   # Product inventory management
│   ├── cart_model.py                      # Shopping cart functionality
│   ├── order_model.py                     # Order processing
│   ├── appointment_model.py               # Appointment scheduling
│   ├── adoption_model.py                  # Adoption request handling
│   ├── attendance_model.py                # Attendace management
│   └── surrender_model.py                 # Surrender request management
└── main.py                                # Application entry point
```

---

## 🖼️ Screenshots

| **Panel** | **Description** | **Screenshot** |
|-----------|-----------------|----------------|
| **Login Window** | Secure authentication with role-based access | <img width="940" height="500" alt="image" src="https://github.com/user-attachments/assets/7c46e53c-ed1e-43f1-9231-f3e2d11a861a" />
" /> |
| **Pet Management** | Complete CRUD operations for pet inventory | <img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/68d16d55-9d8e-4fe7-9762-03a7ba7aee94" />
" /> |
| **Product Catalog** | Browse products with search and filtering | <img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/770b0f87-d8b1-43ff-9f1f-982f409a2d0f" />
" /> |
| **Shopping Cart** | Manage cart items and proceed to checkout | <img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/81cc5666-cf38-40f0-b73c-2695da7c050a" />
" /> |
| **Appointment Booking** | Schedule pet services with date/time selection | <img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/87cf42f0-88bf-4535-b780-0a0c68d5e563" />
" /> |
| **Order History** | Track past purchases with status updates | <img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/043b8c8a-1d80-48d0-bc47-200e4754cc19" />
" /> |

---

## 🔧 Technical Details

### **Database Design**
The system uses a relational database with the following key tables:
- `users` - User accounts with role-based permissions
- `pets` - Pet inventory with status tracking
- `products` - Product catalog with stock management
- `orders` - Customer orders with payment details
- `appointments` - Service bookings with time slots
- `adoption_requests` - Adoption applications
- `surrender_requests` - Pet surrender requests
- `order_items` - Pet surrender requests
- `cart` - cart management
- `attendance` - Staff attendance management

### **Architecture Patterns**
- **Model-View-Controller (MVC)** - Separates data (models), UI (views), and logic
- **Repository Pattern** - Encapsulates database operations in model classes
- **Observer Pattern** - Uses PyQt6 signals for UI updates

### **Key Algorithms & Data Structures**
- **Form Validation** - Input sanitization and verification
- **Search Algorithms** - Filter products/pets by multiple criteria
- **Date/Time Management** - Appointment scheduling with conflict detection
- **Shopping Cart Logic** - Quantity management and total calculation

---

## 📊 Entity-Relationship Diagram (ERD)

| **Diagram Type**                      | **Description**                                                                                                                                                                   | **Preview**                                                                                                                               |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Entity-Relationship Diagram (ERD)** | Illustrates the database entities, their attributes, and the relationships between tables. This ERD represents the complete database structure of the Pet Shop Management System. | <img width="809" height="1454" alt="ERD Diagram" src="https://github.com/user-attachments/assets/8d1a124f-900d-4f7c-a69b-6b020bba3b8e" /> |

---

## 🚀 Future Enhancements
- **Mobile Companion App** - Extend functionality to mobile devices
- **Online Payment Integration** - Add credit card/PayPal processing
- **Real-time Notifications** - Email/SMS alerts for order updates
- **Advanced Analytics** - Sales reports and business intelligence
- **Multi-store Support** - Manage multiple pet shop locations
- **API Integration** - Connect with veterinary services and suppliers

---

## 📞 Contact & Support
- **GitHub Repository**: https://github.com/kian-2268/Pet-Shop-Python
- **Issues**: Report bugs or feature requests via GitHub Issues
- **Documentation**: Comprehensive documentation available in the repository

---

## 📄 License
This project is developed for educational purposes and can be extended for commercial use with proper modifications.
