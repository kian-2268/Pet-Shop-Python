# models/user_model.py
import mysql.connector
from mysql.connector import Error
from datetime import datetime

class UserModel:
    def __init__(self, db=None):
        self.db = db
        self.connection = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='cuddle_corner',
                autocommit=False
            )
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except Error:
            # Try alternative database name
            try:
                self.connection = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='petshop_db',
                    autocommit=False
                )
                self.cursor = self.connection.cursor(dictionary=True)
                return True
            except Error:
                return False
    
    def _ensure_connection(self):
        if self.connection is None or not self.connection.is_connected():
            if not self._connect():
                raise Exception("Failed to establish database connection")
        if self.cursor is None:
            self.cursor = self.connection.cursor(dictionary=True)
    
    def get_user_by_id(self, user_id):
        try:
            self._ensure_connection()
            query = "SELECT * FROM users WHERE id = %s"
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchone()
        except Error:
            return None
    
    def update_user(self, user_id, update_data):
        try:
            if not update_data:
                return False
        
            self._ensure_connection()
        
            # Build the SET clause
            set_parts = []
            values = []
        
            # Map data keys to database column names
            for key, value in update_data.items():
                if key in ['first_name', 'last_name', 'email', 'phone', 'address', 'username']:
                    set_parts.append(f"{key} = %s")
                    values.append(value)
        
            if not set_parts:
                return False
            
            # Add user_id to values
            values.append(user_id)
        
            # Create the query
            set_clause = ", ".join(set_parts)
            query = f"UPDATE users SET {set_clause} WHERE id = %s"
        
            self.cursor.execute(query, values)
            self.connection.commit()
        
            return self.cursor.rowcount > 0
            
        except Exception:
            try:
                if self.connection:
                    self.connection.rollback()
            except:
                pass
            return False
    
    def update_profile_image(self, user_id, image_path):
        try:
            self._ensure_connection()
            query = "UPDATE users SET profile_image = %s WHERE id = %s"
            self.cursor.execute(query, (image_path, user_id))
            self.connection.commit()
            return True
        except Exception:
            return False
    
    def update_password(self, user_id, new_password):
        try:
            self._ensure_connection()
            query = "UPDATE users SET password = %s WHERE id = %s"
            self.cursor.execute(query, (new_password, user_id))
            self.connection.commit()
            return True
        except Exception:
            return False
    
    def authenticate(self, username, password):
        try:
            self._ensure_connection()
            
            # First try to get user by username
            query = "SELECT * FROM users WHERE username = %s"
            self.cursor.execute(query, (username,))
            user = self.cursor.fetchone()
            
            if not user:
                # Try by email
                query = "SELECT * FROM users WHERE email = %s"
                self.cursor.execute(query, (username,))
                user = self.cursor.fetchone()
            
            if user:
                # Check password (in production, use hashed password comparison)
                if user.get('password') == password:
                    # Check if user is active
                    if user.get('is_active', 1) == 1:
                        return user
            
            return None
            
        except Exception:
            return None
    
    def get_user_by_email(self, email):
        try:
            self._ensure_connection()
            query = "SELECT * FROM users WHERE email = %s"
            self.cursor.execute(query, (email,))
            return self.cursor.fetchone()
        except Error:
            return None
    
    def get_user_by_username(self, username):
        try:
            self._ensure_connection()
            query = "SELECT * FROM users WHERE username = %s"
            self.cursor.execute(query, (username,))
            return self.cursor.fetchone()
        except Error:
            return None
    
    def create_user(self, user_data):
        try:
            self._ensure_connection()
            
            # Check if username already exists
            if self.get_user_by_username(user_data.get('username')):
                return None
            
            # Check if email already exists
            if self.get_user_by_email(user_data.get('email')):
                return None
            
            query = """
                INSERT INTO users 
                (username, password, email, first_name, last_name, phone, address, role, created_at, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                user_data.get('username'),
                user_data.get('password'),
                user_data.get('email'),
                user_data.get('first_name'),
                user_data.get('last_name'),
                user_data.get('phone'),
                user_data.get('address'),
                user_data.get('role', 'staff'),
                datetime.now(),
                user_data.get('is_active', 1)
            )
            
            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.lastrowid
            
        except Exception:
            try:
                if self.connection:
                    self.connection.rollback()
            except:
                pass
            return None
    
    def toggle_user_status(self, user_id, is_active):
        try:
            self._ensure_connection()
            query = "UPDATE users SET is_active = %s WHERE id = %s"
            self.cursor.execute(query, (1 if is_active else 0, user_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Exception:
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_all_users(self, role_filter=None):
        try:
            self._ensure_connection()
            
            if role_filter:
                query = "SELECT * FROM users WHERE role = %s ORDER BY id"
                self.cursor.execute(query, (role_filter,))
            else:
                query = "SELECT * FROM users ORDER BY id"
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
        except Exception:
            return []
    
    def refresh_user(self, user_id):
        try:
            # Close and reopen connection
            self.close()
            self._connect()
        
            # Fetch fresh user data
            return self.get_user_by_id(user_id)
        except Exception:
            return None
    
    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception:
            pass
