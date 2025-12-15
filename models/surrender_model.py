class SurrenderModel:
    def __init__(self, db):
        self.db = db
    
    def create_surrender_request(self, request_data):
        query = """
        INSERT INTO surrender_requests (customer_id, pet_name, species, breed, age, reason)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (
            request_data['customer_id'],
            request_data['pet_name'],
            request_data['species'],
            request_data['breed'],
            request_data['age'],
            request_data['reason']
        )
        
        return self.db.execute_query(query, params)
    
    def get_surrender_requests_by_customer(self, customer_id):
        query = """
        SELECT * FROM surrender_requests 
        WHERE customer_id = %s 
        ORDER BY request_date DESC
        """
        return self.db.execute_query(query, (customer_id,))
    
    def get_all_surrender_requests(self, status=None):
        if status:
            query = """
            SELECT sr.*, u.first_name, u.last_name, u.email
            FROM surrender_requests sr
            JOIN users u ON sr.customer_id = u.id
            WHERE sr.status = %s
            ORDER BY sr.request_date DESC
            """
            return self.db.execute_query(query, (status,))
        else:
            query = """
            SELECT sr.*, u.first_name, u.last_name, u.email
            FROM surrender_requests sr
            JOIN users u ON sr.customer_id = u.id
            ORDER BY sr.request_date DESC
            """
            return self.db.execute_query(query)
    
    def update_surrender_status(self, request_id, status, approved_by=None):
        query = "UPDATE surrender_requests SET status = %s, approved_by = %s WHERE id = %s"
        return self.db.execute_query(query, (status, approved_by, request_id))
