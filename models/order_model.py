class OrderModel:
    def __init__(self, db):
        self.db = db
    
    def create_order(self, customer_id, staff_id, items, total_amount, 
                     payment_method='Cash', order_status='Pending', notes=None):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            # Create order with all columns
            order_query = """
            INSERT INTO orders (customer_id, staff_id, total_amount, status, 
                               payment_method, payment_status, notes)
            VALUES (%s, %s, %s, %s, %s, 'Paid', %s)
            """
            cursor.execute(order_query, (customer_id, staff_id, total_amount, 
                                        order_status, payment_method, notes))
            order_id = cursor.lastrowid
            
            # Add order items and update inventory
            for item in items:
                if 'product_id' in item:
                    # Product order
                    item_query = """
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(item_query, (order_id, item['product_id'], 
                                               item['quantity'], item['price']))
                    
                    # Update product quantity
                    update_query = "UPDATE products SET quantity = quantity - %s WHERE id = %s"
                    cursor.execute(update_query, (item['quantity'], item['product_id']))
                
                elif 'pet_id' in item:
                    # Pet order
                    item_query = """
                    INSERT INTO order_items (order_id, pet_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(item_query, (order_id, item['pet_id'], 1, item['price']))
                    
                    # Update pet status
                    update_query = "UPDATE pets SET status = 'Sold' WHERE id = %s"
                    cursor.execute(update_query, (item['pet_id'],))
            
            connection.commit()
            cursor.close()
            return order_id
            
        except Exception as e:
            connection.rollback()
            print(f"Error creating order: {e}")
            return None
    
    def update_order_status(self, order_id, status, staff_id=None):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            if staff_id:
                query = "UPDATE orders SET status = %s, staff_id = %s WHERE id = %s"
                cursor.execute(query, (status, staff_id, order_id))
            else:
                query = "UPDATE orders SET status = %s WHERE id = %s"
                cursor.execute(query, (status, order_id))
            
            connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"Error updating order status: {e}")
            return False
    
    def update_order_notes(self, order_id, notes):
        try:
            query = "UPDATE orders SET notes = %s WHERE id = %s"
            self.db.execute_update(query, (notes, order_id))
            return True
        except Exception as e:
            print(f"Error updating order notes: {e}")
            return False
    
    def get_order_by_id(self, order_id):
        query = """
        SELECT o.*, 
               staff.first_name as staff_first_name, 
               staff.last_name as staff_last_name,
               customer.username as customer_username,
               customer.first_name as customer_first_name,
               customer.last_name as customer_last_name
        FROM orders o
        LEFT JOIN users staff ON o.staff_id = staff.id
        LEFT JOIN users customer ON o.customer_id = customer.id
        WHERE o.id = %s
        """
        result = self.db.execute_query(query, (order_id,))
        return result[0] if result else None
    
    def get_orders_by_customer(self, customer_id):
        query = """
        SELECT o.*, 
               u.first_name as staff_first_name, 
               u.last_name as staff_last_name 
        FROM orders o 
        LEFT JOIN users u ON o.staff_id = u.id 
        WHERE o.customer_id = %s 
        ORDER BY o.order_date DESC
        """
        return self.db.execute_query(query, (customer_id,))
    
    def get_order_details(self, order_id):
        query = """
        SELECT oi.*, 
               COALESCE(p.name, pt.name) as item_name,
               COALESCE(p.image_path, pt.image_path) as image_path,
               CASE WHEN p.id IS NOT NULL THEN 'product' ELSE 'pet' END as item_type,
               p.description as product_description,
               pt.species as pet_species,
               pt.breed as pet_breed
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.id
        LEFT JOIN pets pt ON oi.pet_id = pt.id
        WHERE oi.order_id = %s
        """
        return self.db.execute_query(query, (order_id,))
    
    def get_all_orders(self, status=None, customer_id=None):
        if status and customer_id:
            query = """
            SELECT o.*, 
                   staff.first_name as staff_first_name, 
                   staff.last_name as staff_last_name,
                   customer.username as customer_username
            FROM orders o
            LEFT JOIN users staff ON o.staff_id = staff.id
            LEFT JOIN users customer ON o.customer_id = customer.id
            WHERE o.status = %s AND o.customer_id = %s
            ORDER BY o.order_date DESC
            """
            return self.db.execute_query(query, (status, customer_id))
        elif status:
            query = """
            SELECT o.*, 
                   staff.first_name as staff_first_name, 
                   staff.last_name as staff_last_name,
                   customer.username as customer_username
            FROM orders o
            LEFT JOIN users staff ON o.staff_id = staff.id
            LEFT JOIN users customer ON o.customer_id = customer.id
            WHERE o.status = %s
            ORDER BY o.order_date DESC
            """
            return self.db.execute_query(query, (status,))
        elif customer_id:
            query = """
            SELECT o.*, 
                   staff.first_name as staff_first_name, 
                   staff.last_name as staff_last_name,
                   customer.username as customer_username
            FROM orders o
            LEFT JOIN users staff ON o.staff_id = staff.id
            LEFT JOIN users customer ON o.customer_id = customer.id
            WHERE o.customer_id = %s
            ORDER BY o.order_date DESC
            """
            return self.db.execute_query(query, (customer_id,))
        else:
            query = """
            SELECT o.*, 
                   staff.first_name as staff_first_name, 
                   staff.last_name as staff_last_name,
                   customer.username as customer_username
            FROM orders o
            LEFT JOIN users staff ON o.staff_id = staff.id
            LEFT JOIN users customer ON o.customer_id = customer.id
            ORDER BY o.order_date DESC
            """
            return self.db.execute_query(query)
    
    def delete_order(self, order_id):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            # First, restore inventory from order items
            items_query = """
            SELECT product_id, pet_id, quantity 
            FROM order_items 
            WHERE order_id = %s
            """
            cursor.execute(items_query, (order_id,))
            items = cursor.fetchall()
            
            for item in items:
                if item['product_id']:
                    # Restore product quantity
                    restore_query = """
                    UPDATE products 
                    SET quantity = quantity + %s 
                    WHERE id = %s
                    """
                    cursor.execute(restore_query, (item['quantity'], item['product_id']))
                elif item['pet_id']:
                    # Restore pet status
                    restore_query = "UPDATE pets SET status = 'Available' WHERE id = %s"
                    cursor.execute(restore_query, (item['pet_id'],))
            
            # Delete order items
            delete_items_query = "DELETE FROM order_items WHERE order_id = %s"
            cursor.execute(delete_items_query, (order_id,))
            
            # Delete the order
            delete_order_query = "DELETE FROM orders WHERE id = %s"
            cursor.execute(delete_order_query, (order_id,))
            
            connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"Error deleting order: {e}")
            return False
