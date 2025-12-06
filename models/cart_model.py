class CartModel:
    def __init__(self, db):
        self.db = db
    
    def get_cart_items(self, customer_id):
        query = """
        SELECT c.*, 
               COALESCE(p.name, pt.name) as item_name,
               COALESCE(p.price, pt.price) as price,
               COALESCE(p.image_path, pt.image_path) as image_path,
               CASE WHEN p.id IS NOT NULL THEN 'product' ELSE 'pet' END as item_type,
               p.id as product_id,
               pt.id as pet_id
        FROM cart c
        LEFT JOIN products p ON c.product_id = p.id
        LEFT JOIN pets pt ON c.pet_id = pt.id
        WHERE c.customer_id = %s
        ORDER BY c.added_at DESC
        """
        result = self.db.execute_query(query, (customer_id,))
        return result if result else []
    
    def add_to_cart(self, customer_id, item_type, item_id, quantity=1):
        if item_type == 'product':
            check_query = """
            SELECT id, quantity FROM cart 
            WHERE customer_id = %s AND product_id = %s
            """
            existing = self.db.execute_query(check_query, (customer_id, item_id))
            
            if existing:
                new_quantity = existing[0]['quantity'] + quantity
                update_query = "UPDATE cart SET quantity = %s WHERE id = %s"
                return self.db.execute_query(update_query, (new_quantity, existing[0]['id']))
            else:
                query = """
                INSERT INTO cart (customer_id, product_id, quantity)
                VALUES (%s, %s, %s)
                """
        else:
            check_query = """
            SELECT id FROM cart 
            WHERE customer_id = %s AND pet_id = %s
            """
            existing = self.db.execute_query(check_query, (customer_id, item_id))
            
            if existing:
                return False
            
            query = """
            INSERT INTO cart (customer_id, pet_id, quantity)
            VALUES (%s, %s, %s)
            """
        
        result = self.db.execute_query(query, (customer_id, item_id, quantity))
        return result is not False
    
    def update_cart_quantity(self, cart_id, quantity):
        if quantity <= 0:
            return self.remove_from_cart(cart_id)
        
        query = "UPDATE cart SET quantity = %s WHERE id = %s"
        result = self.db.execute_query(query, (quantity, cart_id))
        return result is not False
    
    def remove_from_cart(self, cart_id):
        query = "DELETE FROM cart WHERE id = %s"
        result = self.db.execute_query(query, (cart_id,))
        return result is not False
    
    def clear_cart(self, customer_id):
        query = "DELETE FROM cart WHERE customer_id = %s"
        result = self.db.execute_query(query, (customer_id,))
        return result is not False
    
    def get_cart_total(self, customer_id):
        items = self.get_cart_items(customer_id)
        total = 0
        for item in items:
            total += item['price'] * item['quantity']
        return total