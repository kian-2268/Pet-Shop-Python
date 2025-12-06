from datetime import datetime, timedelta

class AttendanceModel:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def check_in(self, user_id):
        try:
            today = datetime.now().date()
            current_time = datetime.now()
            
            query = "SELECT id FROM attendance WHERE staff_id = %s AND date = %s"
            result = self.db.execute_query(query, (user_id, today))
            
            if result and len(result) > 0:
                return False  # Already checked in today
            
            # Insert new record
            insert_query = """
                INSERT INTO attendance (staff_id, date, check_in, check_out, hours_worked)
                VALUES (%s, %s, %s, %s, %s)
            """
            success = self.db.execute_query(insert_query, (user_id, today, current_time, None, None))
            return bool(success)
            
        except Exception as e:
            print(f"Error during check-in: {e}")
            return False
    
    def check_out(self, user_id):
        try:
            today = datetime.now().date()
            current_time = datetime.now()
            
            query = "SELECT id, check_in FROM attendance WHERE staff_id = %s AND date = %s AND check_out IS NULL"
            result = self.db.execute_query(query, (user_id, today))
            
            if not result or len(result) == 0:
                return False 
            
            # Extract data from dictionary
            record = result[0]
            record_id = record['id']
            check_in_time = record['check_in']
            
            if not check_in_time:
                return False
            
            # Calculate hours worked
            hours_worked = (current_time - check_in_time).total_seconds() / 3600.0
            
            # Update the record
            update_query = """
                UPDATE attendance 
                SET check_out = %s, hours_worked = %s 
                WHERE id = %s
            """
            success = self.db.execute_query(update_query, (current_time, hours_worked, record_id))
            return bool(success)
            
        except Exception as e:
            print(f"Error during check-out: {e}")
            return False
    
    def get_attendance_by_date(self, user_id, date):
        try:
            query = """
                SELECT id, staff_id, date, check_in, check_out, hours_worked 
                FROM attendance 
                WHERE staff_id = %s AND date = %s
            """
            result = self.db.execute_query(query, (user_id, date))
            
            if result and len(result) > 0:
                record = result[0]
                return {
                    'id': record['id'],
                    'staff_id': record['staff_id'],
                    'date': record['date'],
                    'check_in': record['check_in'],
                    'check_out': record['check_out'],
                    'hours_worked': record['hours_worked']
                }
            return None
            
        except Exception as e:
            print(f"Error fetching attendance by date: {e}")
            return None
    
    def get_attendance_by_month(self, user_id, month_start):
        try:
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1)
            month_end = month_end - timedelta(days=1)
            
            query = """
                SELECT id, staff_id, date, check_in, check_out, hours_worked 
                FROM attendance 
                WHERE staff_id = %s AND date BETWEEN %s AND %s 
                ORDER BY date DESC
            """
            result = self.db.execute_query(query, (user_id, month_start, month_end))
            
            attendance = []
            if result:
                for record in result:
                    attendance.append({
                        'id': record['id'],
                        'staff_id': record['staff_id'],
                        'date': record['date'],
                        'check_in': record['check_in'],
                        'check_out': record['check_out'],
                        'hours_worked': record['hours_worked']
                    })
            
            return attendance
            
        except Exception as e:
            print(f"Error fetching attendance by month: {e}")
            return []