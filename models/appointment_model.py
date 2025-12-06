from datetime import datetime

class AppointmentModel:
    def __init__(self, db):
        self.db = db
    
    def create_appointment(self, appointment_data):
        query = """
        INSERT INTO appointments (customer_id, staff_id, service_type, appointment_date, notes)
        VALUES (%s, %s, %s, %s, %s)
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
        SELECT a.*, u.first_name as staff_first_name, u.last_name as staff_last_name
        FROM appointments a
        LEFT JOIN users u ON a.staff_id = u.id
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
    
    def update_appointment_status(self, appointment_id, new_status):
        query = "UPDATE appointments SET status = %s WHERE id = %s"
        return self.db.execute_query(query, (new_status, appointment_id))
    
    def assign_staff(self, appointment_id, staff_id):
        query = "UPDATE appointments SET staff_id = %s WHERE id = %s"
        return self.db.execute_query(query, (staff_id, appointment_id))
    
    def get_available_time_slots(self, date, staff_id=None):
        # Retrieve existing appointments for the date
        if staff_id:
            query = """
            SELECT appointment_date FROM appointments 
            WHERE DATE(appointment_date) = %s AND staff_id = %s AND status IN ('Pending', 'Approved')
            """
            params = (date, staff_id)
        else:
            query = """
            SELECT appointment_date FROM appointments 
            WHERE DATE(appointment_date) = %s AND status IN ('Pending', 'Approved')
            """
            params = (date,)
        
        existing_appointments = self.db.execute_query(query, params)
        
        base_date = datetime.strptime(date, '%Y-%m-%d')
        time_slots = []
        
        for hour in range(9, 17): 
            for minute in [0, 30]:
                slot_time = base_date.replace(hour=hour, minute=minute)
                time_slots.append(slot_time)
        
        booked_times = [datetime.strptime(apt['appointment_date'], '%Y-%m-%d %H:%M:%S') for apt in existing_appointments]
        available_slots = [slot for slot in time_slots if slot not in booked_times]
        
        return available_slots