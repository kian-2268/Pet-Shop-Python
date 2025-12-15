import os
import shutil
from datetime import datetime

class ProductModel:
    def __init__(self, db):
        self.db = db
        self.image_base_path = "product_images"
        
        # Create image directory if it doesn't exist
        if not os.path.exists(self.image_base_path):
            os.makedirs(self.image_base_path)
    
    def get_all_products(self, category=None):
        if category and category != "All":
            query = "SELECT * FROM products WHERE category = %s ORDER BY name"
            return self.db.execute_query(query, (category,))
        else:
            query = "SELECT * FROM products ORDER BY name"
            return self.db.execute_query(query)
    
    def get_product_by_id(self, product_id):
        query = "SELECT * FROM products WHERE id = %s"
        result = self.db.execute_query(query, (product_id,))
        return result[0] if result else None
    
    def add_product(self, product_data):
        # Handle image upload
        image_path = None
        if product_data.get('image_path'):
            image_path = self.save_image(product_data['image_path'])
        
        query = """
        INSERT INTO products (name, category, description, price, quantity, reorder_level, image_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            product_data['name'], product_data['category'], product_data['description'],
            product_data['price'], product_data['quantity'], product_data['reorder_level'],
            image_path
        )
        
        return self.db.execute_query(query, params)
    
    def update_product(self, product_id, product_data):
        # Get current product data
        current_product = self.get_product_by_id(product_id)
        
        # Handle image update
        image_path = current_product['image_path']
        if product_data.get('image_path') and product_data['image_path'] != current_product['image_path']:
            # Delete old image if exists
            if current_product['image_path'] and os.path.exists(current_product['image_path']):
                os.remove(current_product['image_path'])
            image_path = self.save_image(product_data['image_path'])
        
        query = """
        UPDATE products SET name = %s, category = %s, description = %s, price = %s,
                       quantity = %s, reorder_level = %s, image_path = %s
        WHERE id = %s
        """
        
        params = (
            product_data['name'], product_data['category'], product_data['description'],
            product_data['price'], product_data['quantity'], product_data['reorder_level'],
            image_path, product_id
        )
        
        return self.db.execute_query(query, params)
    
    def delete_product(self, product_id):
        # Get product data to delete image
        product = self.get_product_by_id(product_id)
        if product and product['image_path'] and os.path.exists(product['image_path']):
            os.remove(product['image_path'])
        
        query = "DELETE FROM products WHERE id = %s"
        return self.db.execute_query(query, (product_id,))
    
    def update_quantity(self, product_id, new_quantity):
        query = "UPDATE products SET quantity = %s WHERE id = %s"
        return self.db.execute_query(query, (new_quantity, product_id))
    
    def get_low_stock_products(self):
        query = "SELECT * FROM products WHERE quantity <= reorder_level ORDER BY quantity ASC"
        return self.db.execute_query(query)
    
    def save_image(self, source_path):
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"product_{timestamp}_{os.path.basename(source_path)}"
            destination_path = os.path.join(self.image_base_path, filename)
            
            # Copy file
            shutil.copy2(source_path, destination_path)
            return destination_path
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
