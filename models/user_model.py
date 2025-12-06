class UserModel:
    def __init__(self, db):
        self.db = db
    
    def authenticate(self, username, password):
        """Authenticate user with plain text passwords"""
        try:
            query = "SELECT id, username, role FROM users WHERE username = %s AND password = %s"
            result = self.db.execute_query(query, (username, password))
            if result:
                user = result[0]
                return {
                    'user_id': user['id'],
                    'username': user['username'],
                    'role': user['role']
                }
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE id = %s"
        result = self.db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def create_user(self, username, password, email, first_name, last_name, phone, address, role='customer'):
        """Create a new user with plain text password"""
        query = """
        INSERT INTO users (username, password, email, first_name, last_name, phone, address, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (username, password, email, first_name, last_name, phone, address, role))
    
    def update_user(self, user_id, user_data):
        query = """
        UPDATE users SET email = %s, first_name = %s, last_name = %s, phone = %s, address = %s 
        WHERE id = %s
        """
        return self.db.execute_query(query, (*user_data, user_id))
    
    def get_all_users(self, role=None):
        if role:
            query = "SELECT * FROM users WHERE role = %s"
            return self.db.execute_query(query, (role,))
        else:
            query = "SELECT * FROM users"
            return self.db.execute_query(query)
    
    def deactivate_user(self, user_id):
        query = "UPDATE users SET is_active = FALSE WHERE id = %s"
        return self.db.execute_query(query, (user_id,))
    
    def user_exists(self, username=None, email=None):
        """Check if a user already exists"""
        if username:
            query = "SELECT id FROM users WHERE username = %s"
            result = self.db.execute_query(query, (username,))
            return bool(result)
        elif email:
            query = "SELECT id FROM users WHERE email = %s"
            result = self.db.execute_query(query, (email,))
            return bool(result)
        return False
    
    # Password Reset Methods
    def get_user_by_email(self, email):
        """Get user by email address"""
        try:
            query = "SELECT id, username, email FROM users WHERE email = %s"
            result = self.db.execute_query(query, (email,))
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def set_reset_token(self, email, reset_token, expiry):
        """Store password reset token in the database"""
        try:
            query = "UPDATE users SET reset_token = %s, reset_token_expiry = %s WHERE email = %s"
            self.db.execute_query(query, (reset_token, expiry, email))
            return True
        except Exception as e:
            print(f"Error setting reset token: {e}")
            return False
    
    def verify_reset_token(self, email, token):
        """Verify if reset token is valid and not expired"""
        try:
            query = """
            SELECT id FROM users 
            WHERE email = %s AND reset_token = %s AND reset_token_expiry > NOW()
            """
            result = self.db.execute_query(query, (email, token))
            return len(result) > 0
        except Exception as e:
            print(f"Error verifying reset token: {e}")
            return False
    
    def update_password(self, email, new_password):
        """Update user password and clear reset token"""
        try:
            query = """
            UPDATE users 
            SET password = %s, reset_token = NULL, reset_token_expiry = NULL 
            WHERE email = %s
            """
            self.db.execute_query(query, (new_password, email))
            return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False