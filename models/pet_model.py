import os
import shutil
from datetime import datetime

class PetModel:
    def __init__(self, db):
        self.db = db
        self.image_base_path = "pet_images"
        
        if not os.path.exists(self.image_base_path):
            os.makedirs(self.image_base_path)
    
    def get_all_pets(self, status=None):
        if status:
            query = "SELECT * FROM pets WHERE status = %s ORDER BY created_at DESC"
            return self.db.execute_query(query, (status,))
        else:
            query = "SELECT * FROM pets ORDER BY created_at DESC"
            return self.db.execute_query(query)
    
    def get_pet_by_id(self, pet_id):
        query = "SELECT * FROM pets WHERE id = %s"
        result = self.db.execute_query(query, (pet_id,))
        return result[0] if result else None
    
    def add_pet(self, pet_data, created_by):
        image_path = None
        if pet_data.get('image_path'):
            image_path = self.save_image(pet_data['image_path'])
        
        query = """
        INSERT INTO pets (name, species, breed, age, gender, price, description, 
                         image_path, status, health_status, vaccination_status, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            pet_data['name'], pet_data['species'], pet_data['breed'],
            pet_data['age'], pet_data['gender'], pet_data['price'],
            pet_data['description'], image_path, pet_data['status'],
            pet_data['health_status'], pet_data['vaccination_status'], created_by
        )
        
        return self.db.execute_query(query, params)
    
    def update_pet(self, pet_id, pet_data):
        current_pet = self.get_pet_by_id(pet_id)
        
        image_path = current_pet['image_path']
        if pet_data.get('image_path') and pet_data['image_path'] != current_pet['image_path']:
            if current_pet['image_path'] and os.path.exists(current_pet['image_path']):
                os.remove(current_pet['image_path'])
            image_path = self.save_image(pet_data['image_path'])
        
        query = """
        UPDATE pets SET name = %s, species = %s, breed = %s, age = %s, gender = %s,
                       price = %s, description = %s, image_path = %s, status = %s,
                       health_status = %s, vaccination_status = %s
        WHERE id = %s
        """
        
        params = (
            pet_data['name'], pet_data['species'], pet_data['breed'],
            pet_data['age'], pet_data['gender'], pet_data['price'],
            pet_data['description'], image_path, pet_data['status'],
            pet_data['health_status'], pet_data['vaccination_status'], pet_id
        )
        
        return self.db.execute_query(query, params)
    
    def delete_pet(self, pet_id):
        pet = self.get_pet_by_id(pet_id)
        if pet and pet['image_path'] and os.path.exists(pet['image_path']):
            os.remove(pet['image_path'])
        
        query = "DELETE FROM pets WHERE id = %s"
        return self.db.execute_query(query, (pet_id,))
    
    def save_image(self, source_path):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pet_{timestamp}_{os.path.basename(source_path)}"
            destination_path = os.path.join(self.image_base_path, filename)
            
            shutil.copy2(source_path, destination_path)
            return destination_path
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    
    def search_pets(self, search_term):
        query = """
        SELECT * FROM pets 
        WHERE name LIKE %s OR species LIKE %s OR breed LIKE %s 
        ORDER BY created_at DESC
        """
        search_pattern = f"%{search_term}%"
        return self.db.execute_query(query, (search_pattern, search_pattern, search_pattern))