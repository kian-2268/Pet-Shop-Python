class AdoptionModel:
    def __init__(self, db):
        self.db = db
    
    def create_adoption_request(self, customer_id, pet_id, notes=''):
        query = """
        INSERT INTO adoption_requests (customer_id, pet_id, notes)
        VALUES (%s, %s, %s)
        """
        return self.db.execute_query(query, (customer_id, pet_id, notes))
    
    def get_adoption_requests(self, status=None):
        if status:
            query = """
            SELECT ar.*, u.first_name, u.last_name, u.email, p.name as pet_name, p.species
            FROM adoption_requests ar
            JOIN users u ON ar.customer_id = u.id
            JOIN pets p ON ar.pet_id = p.id
            WHERE ar.status = %s
            ORDER BY ar.request_date DESC
            """
            return self.db.execute_query(query, (status,))
        else:
            query = """
            SELECT ar.*, u.first_name, u.last_name, u.email, p.name as pet_name, p.species
            FROM adoption_requests ar
            JOIN users u ON ar.customer_id = u.id
            JOIN pets p ON ar.pet_id = p.id
            ORDER BY ar.request_date DESC
            """
            return self.db.execute_query(query)
    
    def update_adoption_status(self, request_id, status, approved_by=None):
        query = "UPDATE adoption_requests SET status = %s, approved_by = %s WHERE id = %s"
        return self.db.execute_query(query, (status, approved_by, request_id))
    
    def get_adoption_requests_by_customer(self, customer_id):
        query = """
        SELECT ar.*, p.name as pet_name, p.species, p.breed
        FROM adoption_requests ar
        JOIN pets p ON ar.pet_id = p.id
        WHERE ar.customer_id = %s
        ORDER BY ar.request_date DESC
        """
        return self.db.execute_query(query, (customer_id,))
    
    def create_adoption_request(self, customer_id, pet_id, notes):
        query = """
        INSERT INTO adoption_requests (customer_id, pet_id, notes, status, request_date)
        VALUES (%s, %s, %s, 'Pending', NOW())
        """
        result = self.db.execute_query(query, (customer_id, pet_id, notes))
        return result is not False
