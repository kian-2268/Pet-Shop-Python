from datetime import datetime, timedelta

class AppointmentModel:
    def __init__(self, db):
        self.db = db
    
    def create_appointment(self, appointment_data):
        # Check if appointment slot is available
        if not self.check_appointment_availability(
            appointment_data['appointment_date'], 
            appointment_data.get('staff_id')
        ):
            return False  # Slot not available
        
        query = """
        INSERT INTO appointments (customer_id, staff_id, service_type, appointment_date, notes, status)
        VALUES (%s, %s, %s, %s, %s, 'Pending')
        """
        
        params = (
            appointment_data['customer_id'],
            appointment_data.get('staff_id'),
            appointment_data['service_type'],
            appointment_data['appointment_date'],
            appointment_data.get('notes', '')
        )
        
        return self.db.execute_query(query, params)
    
    def get_appointments_by_customer(self, customer_id):
        query = """
        SELECT a.*, 
               s.first_name as staff_first_name, 
               s.last_name as staff_last_name,
               c.first_name as customer_first_name,
               c.last_name as customer_last_name
        FROM appointments a
        LEFT JOIN users s ON a.staff_id = s.id
        INNER JOIN users c ON a.customer_id = c.id
        WHERE a.customer_id = %s
        ORDER BY a.appointment_date DESC
        """
        return self.db.execute_query(query, (customer_id,))
    
    def get_all_appointments(self):
        query = """
        SELECT a.*, 
               c.first_name as customer_first_name, c.last_name as customer_last_name,
               s.first_name as staff_first_name, s.last_name as staff_last_name
        FROM appointments a
        LEFT JOIN users c ON a.customer_id = c.id
        LEFT JOIN users s ON a.staff_id = s.id
        ORDER BY a.appointment_date DESC
        """
        return self.db.execute_query(query)
    
    def get_appointment_by_id(self, appointment_id):
        query = """
        SELECT a.*, 
               c.first_name as customer_first_name, c.last_name as customer_last_name, c.email as customer_email,
               s.first_name as staff_first_name, s.last_name as staff_last_name, s.email as staff_email
        FROM appointments a
        LEFT JOIN users c ON a.customer_id = c.id
        LEFT JOIN users s ON a.staff_id = s.id
        WHERE a.id = %s
        """
        result = self.db.execute_query(query, (appointment_id,))
        return result[0] if result else None
    
    def update_appointment_status(self, appointment_id, new_status):
        query = "UPDATE appointments SET status = %s WHERE id = %s"
        return self.db.execute_query(query, (new_status, appointment_id))
    
    def update_appointment(self, appointment_id, update_data):
        if not update_data:
            return False
        
        set_clauses = []
        params = []
        
        for field, value in update_data.items():
            if field in ['staff_id', 'service_type', 'appointment_date', 'notes']:
                set_clauses.append(f"{field} = %s")
                params.append(value)
        
        if not set_clauses:
            return False
        
        params.append(appointment_id)
        query = f"UPDATE appointments SET {', '.join(set_clauses)} WHERE id = %s"
        
        return self.db.execute_query(query, tuple(params))
    
    def assign_staff(self, appointment_id, staff_id):
        query = "UPDATE appointments SET staff_id = %s WHERE id = %s"
        return self.db.execute_query(query, (staff_id, appointment_id))
    
    def check_appointment_availability(self, appointment_date, staff_id=None, duration_minutes=30):
        # Parse the appointment date
        if isinstance(appointment_date, str):
            appointment_datetime = datetime.strptime(appointment_date, '%Y-%m-%d %H:%M:%S')
        else:
            appointment_datetime = appointment_date
        
        end_time = appointment_datetime + timedelta(minutes=duration_minutes)
        
        query = """
        SELECT * FROM appointments 
        WHERE (
            (appointment_date <= %s AND DATE_ADD(appointment_date, INTERVAL %s MINUTE) > %s) OR
            (appointment_date < %s AND DATE_ADD(appointment_date, INTERVAL %s MINUTE) >= %s) OR
            (appointment_date >= %s AND appointment_date < %s)
        )
        AND status IN ('Pending', 'Approved')
        """
        
        if staff_id:
            query += " AND (staff_id = %s OR staff_id IS NULL)"
            params = (appointment_datetime, duration_minutes, appointment_datetime, 
                      end_time, duration_minutes, end_time,
                      appointment_datetime, end_time, staff_id)
        else:
            params = (appointment_datetime, duration_minutes, appointment_datetime, 
                      end_time, duration_minutes, end_time,
                      appointment_datetime, end_time)
        
        conflicting_appointments = self.db.execute_query(query, params)
        return len(conflicting_appointments) == 0
    
    def get_available_time_slots(self, date, staff_id=None, business_hours=(9, 17)):
        # Parse date
        if isinstance(date, str):
            base_date = datetime.strptime(date, '%Y-%m-%d')
        else:
            base_date = date
        
        date_str = base_date.strftime('%Y-%m-%d')
        
        # Get existing appointments
        if staff_id:
            query = """
            SELECT appointment_date FROM appointments 
            WHERE DATE(appointment_date) = %s 
            AND staff_id = %s 
            AND status IN ('Pending', 'Approved')
            """
            params = (date_str, staff_id)
        else:
            query = """
            SELECT appointment_date FROM appointments 
            WHERE DATE(appointment_date) = %s 
            AND status IN ('Pending', 'Approved')
            """
            params = (date_str,)
        
        existing_appointments = self.db.execute_query(query, params)
        
        # Generate time slots (every 30 minutes during business hours)
        start_hour, end_hour = business_hours
        time_slots = []
        
        current_time = base_date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_time = base_date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
        while current_time < end_time:
            time_slots.append(current_time)
            current_time += timedelta(minutes=30)
        
        # Filter out booked slots
        booked_times = []
        for apt in existing_appointments:
            try:
                if isinstance(apt['appointment_date'], str):
                    booked_time = datetime.strptime(apt['appointment_date'], '%Y-%m-%d %H:%M:%S')
                else:
                    booked_time = apt['appointment_date']
                booked_times.append(booked_time)
            except:
                continue
        
        # Remove slots that overlap with existing appointments
        available_slots = []
        for slot in time_slots:
            slot_end = slot + timedelta(minutes=30)
            is_available = True
            
            for booked in booked_times:
                booked_end = booked + timedelta(minutes=30)
                # Check for overlap
                if (slot < booked_end and slot_end > booked):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(slot)
        
        return available_slots
    
    def get_appointments_by_date_range(self, start_date, end_date, staff_id=None):
        query = """
        SELECT a.*, 
               c.first_name as customer_first_name, c.last_name as customer_last_name,
               s.first_name as staff_first_name, s.last_name as staff_last_name
        FROM appointments a
        LEFT JOIN users c ON a.customer_id = c.id
        LEFT JOIN users s ON a.staff_id = s.id
        WHERE DATE(a.appointment_date) BETWEEN %s AND %s
        AND a.status IN ('Pending', 'Approved')
        """
        
        if staff_id:
            query += " AND (a.staff_id = %s OR a.staff_id IS NULL)"
            params = (start_date, end_date, staff_id)
        else:
            params = (start_date, end_date)
        
        query += " ORDER BY a.appointment_date ASC"
        return self.db.execute_query(query, params)
    
    def get_appointment_stats(self, start_date=None, end_date=None):
        base_query = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled
        FROM appointments
        """
        
        if start_date and end_date:
            query = base_query + " WHERE DATE(appointment_date) BETWEEN %s AND %s"
            params = (start_date, end_date)
        else:
            query = base_query
            params = ()
        
        result = self.db.execute_query(query, params)
        return result[0] if result else None
    
    def get_service_type_stats(self):
        query = """
        SELECT service_type, COUNT(*) as count
        FROM appointments
        GROUP BY service_type
        ORDER BY count DESC
        """
        return self.db.execute_query(query)
    
    def get_todays_appointments(self):
        today = datetime.now().strftime('%Y-%m-%d')
        query = """
        SELECT a.*, 
               c.first_name as customer_first_name, c.last_name as customer_last_name,
               s.first_name as staff_first_name, s.last_name as staff_last_name
        FROM appointments a
        LEFT JOIN users c ON a.customer_id = c.id
        LEFT JOIN users s ON a.staff_id = s.id
        WHERE DATE(a.appointment_date) = %s
        AND a.status IN ('Pending', 'Approved')
        ORDER BY a.appointment_date ASC
        """
        return self.db.execute_query(query, (today,))
    
    def get_upcoming_appointments(self, customer_id=None, days=7):
        today = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        if customer_id:
            query = """
            SELECT a.*, 
                   s.first_name as staff_first_name, s.last_name as staff_last_name
            FROM appointments a
            LEFT JOIN users s ON a.staff_id = s.id
            WHERE a.customer_id = %s
            AND DATE(a.appointment_date) BETWEEN %s AND %s
            AND a.status IN ('Pending', 'Approved')
            ORDER BY a.appointment_date ASC
            """
            params = (customer_id, today, end_date)
        else:
            query = """
            SELECT a.*, 
                   c.first_name as customer_first_name, c.last_name as customer_last_name,
                   s.first_name as staff_first_name, s.last_name as staff_last_name
            FROM appointments a
            LEFT JOIN users c ON a.customer_id = c.id
            LEFT JOIN users s ON a.staff_id = s.id
            WHERE DATE(a.appointment_date) BETWEEN %s AND %s
            AND a.status IN ('Pending', 'Approved')
            ORDER BY a.appointment_date ASC
            """
            params = (today, end_date)
        
        return self.db.execute_query(query, params)
    
    def delete_appointment(self, appointment_id):
        query = "DELETE FROM appointments WHERE id = %s"
        return self.db.execute_query(query, (appointment_id,))
    
    def reschedule_appointment(self, appointment_id, new_datetime, staff_id=None):
        # Check if new slot is available
        if not self.check_appointment_availability(new_datetime, staff_id):
            return False
        
        # Update the appointment
        update_data = {'appointment_date': new_datetime}
        if staff_id:
            update_data['staff_id'] = staff_id
        
        return self.update_appointment(appointment_id, update_data)
