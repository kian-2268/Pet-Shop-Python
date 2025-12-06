-- Cuddle Corner Pet Shop Database Schema

-- Users table for authentication and user management
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Store hashed passwords in production
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    role ENUM('customer', 'staff', 'admin') DEFAULT 'customer',
    is_active BOOLEAN DEFAULT TRUE,
    reset_token VARCHAR(255) NULL,
    reset_token_expiry DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pets table for available pets
CREATE TABLE IF NOT EXISTS pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    species VARCHAR(50) NOT NULL,  -- Dog, Cat, Bird, Rabbit, etc.
    breed VARCHAR(100),
    age DECIMAL(4,1) NOT NULL,  -- Age in years, e.g., 2.5
    gender ENUM('Male', 'Female') NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    description TEXT,
    health_status VARCHAR(100) DEFAULT 'Good',
    status ENUM('Available', 'Adopted', 'Pending', 'Not Available') DEFAULT 'Available',
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table for pet supplies
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,  -- Food, Toys, Accessories, etc.
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    image_path VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Cart table for shopping cart functionality
CREATE TABLE IF NOT EXISTS cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_type ENUM('pet', 'product') NOT NULL,
    pet_id INT NULL,
    product_id INT NULL,
    quantity INT NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CHECK (
        (item_type = 'pet' AND pet_id IS NOT NULL AND product_id IS NULL) OR
        (item_type = 'product' AND product_id IS NOT NULL AND pet_id IS NULL)
    )
);

-- Orders table for completed purchases
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status ENUM('Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled') DEFAULT 'Pending',
    payment_method VARCHAR(50),
    shipping_address TEXT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Order items table for individual items in orders
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_type ENUM('pet', 'product') NOT NULL,
    pet_id INT NULL,
    product_id INT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    CHECK (
        (item_type = 'pet' AND pet_id IS NOT NULL AND product_id IS NULL) OR
        (item_type = 'product' AND product_id IS NOT NULL AND pet_id IS NULL)
    )
);

-- Adoption requests table
CREATE TABLE IF NOT EXISTS adoption_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pet_id INT NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected', 'Completed') DEFAULT 'Pending',
    notes TEXT,
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by INT NULL,  -- Staff/Admin who reviewed the request
    review_notes TEXT,
    review_date TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Appointments table for grooming, vet visits, etc.
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pet_id INT NULL,  -- NULL if it's a general consultation
    service_type VARCHAR(100) NOT NULL,  -- Grooming, Vet Checkup, Training, etc.
    appointment_date DATETIME NOT NULL,
    duration_minutes INT DEFAULT 60,
    status ENUM('Scheduled', 'Completed', 'Cancelled', 'No-show') DEFAULT 'Scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE SET NULL
);

-- Pet surrender requests table
CREATE TABLE IF NOT EXISTS surrender_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pet_name VARCHAR(100) NOT NULL,
    species VARCHAR(50) NOT NULL,
    breed VARCHAR(100),
    age DECIMAL(4,1) NOT NULL,
    gender ENUM('Male', 'Female') NOT NULL,
    reason TEXT NOT NULL,
    health_notes TEXT,
    status ENUM('Pending', 'Approved', 'Rejected', 'Completed') DEFAULT 'Pending',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by INT NULL,
    review_notes TEXT,
    review_date TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Inventory table for product stock management
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity_change INT NOT NULL,  -- Positive for additions, negative for sales
    change_type ENUM('Purchase', 'Sale', 'Adjustment', 'Return') NOT NULL,
    notes TEXT,
    changed_by INT NULL,  -- Staff member who made the change
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_pets_species ON pets(species);
CREATE INDEX idx_pets_status ON pets(status);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_cart_user_id ON cart(user_id);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_adoption_requests_status ON adoption_requests(status);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);

-- Insert sample admin user
INSERT IGNORE INTO users (username, password, email, first_name, last_name, role) 
VALUES ('admin', 'admin123', 'admin@cuddlecorner.com', 'System', 'Administrator', 'admin');

-- Insert sample staff user
INSERT IGNORE INTO users (username, password, email, first_name, last_name, role) 
VALUES ('staff', 'staff123', 'staff@cuddlecorner.com', 'Shop', 'Staff', 'staff');

-- Insert sample pets
INSERT IGNORE INTO pets (name, species, breed, age, gender, price, description, health_status, status) VALUES
('Max', 'Dog', 'Golden Retriever', 2.5, 'Male', 450.00, 'Friendly and playful golden retriever. Great with kids and other pets.', 'Excellent', 'Available'),
('Luna', 'Cat', 'Siamese', 1.5, 'Female', 300.00, 'Elegant siamese cat with beautiful blue eyes. Loves attention and cuddles.', 'Good', 'Available'),
('Charlie', 'Dog', 'Beagle', 3.0, 'Male', 350.00, 'Curious and energetic beagle. Great sense of smell and loves outdoor activities.', 'Good', 'Available'),
('Bella', 'Cat', 'Persian', 2.0, 'Female', 400.00, 'Beautiful long-haired persian cat. Calm and gentle temperament.', 'Excellent', 'Available'),
('Rocky', 'Rabbit', 'Holland Lop', 1.0, 'Male', 75.00, 'Adorable holland lop rabbit. Very friendly and easy to handle.', 'Good', 'Available'),
('Coco', 'Bird', 'Parakeet', 0.8, 'Female', 50.00, 'Colorful parakeet that loves to sing and interact.', 'Good', 'Available');

-- Insert sample products
INSERT IGNORE INTO products (name, category, description, price, stock_quantity) VALUES
('Premium Dog Food', 'Food', 'High-quality dog food with balanced nutrition for all breeds', 45.99, 100),
('Cat Litter', 'Supplies', 'Clumping cat litter with odor control', 25.50, 50),
('Pet Carrier', 'Accessories', 'Durable pet carrier for safe transportation', 89.99, 25),
('Chew Toy', 'Toys', 'Durable rubber chew toy for dogs', 15.99, 75),
('Grooming Brush', 'Grooming', 'Professional grooming brush for cats and dogs', 22.75, 30),
('Pet Bed', 'Accessories', 'Comfortable orthopedic pet bed', 65.00, 20);