class OrderModel:
    def __init__(self, db):
        self.db = db
    
    def create_order(self, customer_id, items, total_amount, payment_method='Cash'):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            # Create order
            order_query = """
            INSERT INTO orders (customer_id, total_amount, payment_method, payment_status)
            VALUES (%s, %s, %s, 'Paid')
            """
            cursor.execute(order_query, (customer_id, total_amount, payment_method))
            order_id = cursor.lastrowid
            
            # Add order items and update inventory
            for item in items:
                if 'product_id' in item:
                    # Product order
                    item_query = """
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(item_query, (order_id, item['product_id'], item['quantity'], item['price']))
                    
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
    
    def get_orders_by_customer(self, customer_id):
        query = """
        SELECT o.*, u.first_name, u.last_name 
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
               CASE WHEN p.id IS NOT NULL THEN 'product' ELSE 'pet' END as item_type
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.id
        LEFT JOIN pets pt ON oi.pet_id = pt.id
        WHERE oi.order_id = %s
        """
        return self.db.execute_query(query, (order_id,))
    
    def get_all_orders(self, status=None):
        if status:
            query = """
            SELECT o.*, u.first_name, u.last_name, c.username as customer_name
            FROM orders o
            LEFT JOIN users u ON o.staff_id = u.id
            LEFT JOIN users c ON o.customer_id = c.id
            WHERE o.status = %s
            ORDER BY o.order_date DESC
            """
            return self.db.execute_query(query, (status,))
        else:
            query = """
            SELECT o.*, u.first_name, u.last_name, c.username as customer_name
            FROM orders o
            LEFT JOIN users u ON o.staff_id = u.id
            LEFT JOIN users c ON o.customer_id = c.id
            ORDER BY o.order_date DESC
            """
            return self.db.execute_query(query)