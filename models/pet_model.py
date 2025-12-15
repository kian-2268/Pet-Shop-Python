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
        try:
            pet = self.get_pet_by_id(pet_id)
            if not pet:
                print(f"Pet with ID {pet_id} not found")
                return False
            
            # Check for adoption requests first
            adoption_check = self.db.execute_query(
                "SELECT COUNT(*) as count FROM adoption_requests WHERE pet_id = %s", 
                (pet_id,)
            )
            
            if adoption_check and adoption_check[0]['count'] > 0:
                print(f"Cannot delete pet '{pet['name']}' (ID: {pet_id}) - has {adoption_check[0]['count']} adoption request(s)")
                return False
            
            # Check other possible tables
            tables_to_check = ['sales', 'appointments', 'surrender_requests']
            for table in tables_to_check:
                try:
                    result = self.db.execute_query(
                        f"SELECT COUNT(*) as count FROM {table} WHERE pet_id = %s", 
                        (pet_id,)
                    )
                    if result and result[0]['count'] > 0:
                        print(f"Cannot delete pet '{pet['name']}' (ID: {pet_id}) - has records in {table} table")
                        return False
                except:
                    # Table might not exist, skip
                    pass
            
            # If no related records, proceed with deletion
            query = "DELETE FROM pets WHERE id = %s"
            result = self.db.execute_query(query, (pet_id,))
            
            if result:
                # Delete image if it exists
                if pet.get('image_path') and os.path.exists(pet['image_path']):
                    try:
                        os.remove(pet['image_path'])
                        print(f"Deleted image: {pet['image_path']}")
                    except Exception as e:
                        print(f"Warning: Could not delete image: {e}")
                
                print(f"Successfully deleted pet '{pet['name']}' (ID: {pet_id})")
                return True
            else:
                print(f"Failed to delete pet ID {pet_id}")
                return False
                
        except Exception as e:
            print(f"Error in delete_pet: {e}")
            return False
    
    def archive_pet(self, pet_id):
        """Archive a pet by changing its status instead of deleting"""
        try:
            query = "UPDATE pets SET status = 'Archived' WHERE id = %s"
            result = self.db.execute_query(query, (pet_id,))
            
            if result:
                pet = self.get_pet_by_id(pet_id)
                if pet:
                    print(f"Successfully archived pet '{pet['name']}' (ID: {pet_id})")
                return True
            else:
                print(f"Failed to archive pet ID {pet_id}")
                return False
                
        except Exception as e:
            print(f"Error in archive_pet: {e}")
            return False
    
    def check_pet_has_related_records(self, pet_id):
        """Check if a pet has any related records that would prevent deletion"""
        try:
            # Check adoption_requests table
            adoption_result = self.db.execute_query(
                "SELECT COUNT(*) as count FROM adoption_requests WHERE pet_id = %s", 
                (pet_id,)
            )
            
            if adoption_result and adoption_result[0]['count'] > 0:
                return {
                    'can_delete': False,
                    'message': f"This pet has {adoption_result[0]['count']} adoption request(s)",
                    'adoption_count': adoption_result[0]['count']
                }
            
            # Check other tables that might reference pets
            tables_to_check = ['sales', 'appointments']
            for table in tables_to_check:
                try:
                    result = self.db.execute_query(
                        f"SELECT COUNT(*) as count FROM {table} WHERE pet_id = %s", 
                        (pet_id,)
                    )
                    if result and result[0]['count'] > 0:
                        return {
                            'can_delete': False,
                            'message': f"This pet has records in the {table} table",
                            'table': table,
                            'count': result[0]['count']
                        }
                except:
                    # Table might not exist, skip
                    continue
            
            return {
                'can_delete': True,
                'message': 'This pet can be safely deleted'
            }
            
        except Exception as e:
            print(f"Error checking related records: {e}")
            return {
                'can_delete': False,
                'message': f'Error checking related records: {str(e)}'
            }
    
    def get_adoption_requests_for_pet(self, pet_id):
        try:
            query = """
                SELECT ar.*, u.username as customer_name, u.email, 
                       u.first_name, u.last_name, ar.request_date
                FROM adoption_requests ar
                JOIN users u ON ar.customer_id = u.id
                WHERE ar.pet_id = %s
                ORDER BY ar.request_date DESC
            """
            return self.db.execute_query(query, (pet_id,))
        except Exception as e:
            print(f"Error getting adoption requests: {e}")
            return []
    
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
    
    def force_delete_pet(self, pet_id):
        try:
            pet = self.get_pet_by_id(pet_id)
            if not pet:
                print(f"Pet with ID {pet_id} not found")
                return False
            
            print(f"WARNING: Force deleting pet '{pet['name']}' (ID: {pet_id})")
            
            # Disable foreign key checks
            disable_fk = "SET FOREIGN_KEY_CHECKS = 0"
            self.db.execute_query(disable_fk)
            
            # Delete the pet
            query = "DELETE FROM pets WHERE id = %s"
            result = self.db.execute_query(query, (pet_id,))
            
            # Re-enable foreign key checks
            enable_fk = "SET FOREIGN_KEY_CHECKS = 1"
            self.db.execute_query(enable_fk)
            
            if result:
                # Delete image if it exists
                if pet.get('image_path') and os.path.exists(pet['image_path']):
                    try:
                        os.remove(pet['image_path'])
                    except:
                        pass
                
                print(f"Force deleted pet '{pet['name']}' (ID: {pet_id})")
                print("WARNING: This may have left orphaned records in other tables!")
                return True
            else:
                print(f"Failed to force delete pet ID {pet_id}")
                return False
                
        except Exception as e:
            self.db.execute_query("SET FOREIGN_KEY_CHECKS = 1")
            print(f"Error in force_delete_pet: {e}")
            return False
