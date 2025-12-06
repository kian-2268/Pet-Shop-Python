import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = None
            cls._instance.connect()
        return cls._instance
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'cuddle_corner'),
                port=os.getenv('DB_PORT', '3306')
            )
        except Error as e:
            # Try to create database if it doesn't exist
            self.create_database()
    
    def create_database(self):
        try:
            temp_conn = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                port=os.getenv('DB_PORT', '3306')
            )
            cursor = temp_conn.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS cuddle_corner")
            
            # Use the database
            cursor.execute("USE cuddle_corner")
            
            # Read and execute schema file
            schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
            if os.path.exists(schema_file):
                with open(schema_file, 'r') as file:
                    schema_sql = file.read()
                
                # Execute each statement separately
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        cursor.execute(statement)
            
            temp_conn.commit()
            cursor.close()
            temp_conn.close()
            
            # Reconnect with database
            self.connect()
            
        except Error as e:
            pass
    
    def get_connection(self):
        if self.connection is None or not self.connection.is_connected():
            self.connect()
        return self.connection
    
    def execute_query(self, query, params=None):
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
        
            query_type = query.strip().upper()
        
            if query_type.startswith('SELECT'):
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.rowcount > 0
                if query_type.startswith('INSERT'):
                    result = cursor.lastrowid or True
        
            cursor.close()
            return result
        except Error:
            return False
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()