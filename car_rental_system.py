import mysql.connector
from datetime import datetime
from decimal import Decimal

# Database connection configuration
DB_CONFIG = {
    # Use the correct host/database for your local phpMyAdmin setup.
    # Update 'user' and 'password' to match your MySQL credentials if needed.
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'carrental'
}

def get_db_connection():
    """Establish and return database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# User Management Functions
def register_user(full_name, email, password, role='customer', phone=None, address=None, license_no=None):
    """Register a new user"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sql = """INSERT INTO users (full_name, email, password, role, phone, address, license_no) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (full_name, email, password, role, phone, address, license_no))
            conn.commit()
            print("User registered successfully!")
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error registering user: {err}")
            return None
        finally:
            conn.close()

def login_user(email, password):
    """Authenticate user login"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # First look up the user by email
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                print(f"No user found with email: {email}")
                return None

            # For now passwords are stored in plaintext in this project (not recommended for production)
            # Compare the stored password with the provided one
            stored = user.get('password')
            if stored == password:
                print("Login successful!")
                return user
            else:
                print(f"Password mismatch for user: {email}")
                return None
        finally:
            conn.close()

def list_users():
    """List all users"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Update the query to include phone and other relevant fields
            cursor.execute("""
                SELECT user_id, full_name, email, role, phone, address, license_no 
                FROM users
            """)
            users = cursor.fetchall()
            return users
        finally:
            conn.close()

# Car Management Functions
def add_car(plate_no, brand, model, type, year, color, rate_per_day, seats=4, status='available', image_path=None):
    """Add a new car"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sql = """INSERT INTO cars (plate_no, brand, model, type, year, color, 
                     rate_per_day, seats, status, image_path) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (plate_no, brand, model, type, year, color, 
                               rate_per_day, seats, status, image_path))
            conn.commit()
            print("Car added successfully!")
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error adding car: {err}")
            return None
        finally:
            conn.close()

def update_car(car_id, **kwargs):
    """Update car details"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            sql = f"UPDATE cars SET {set_clause} WHERE car_id = %s"
            values = list(kwargs.values()) + [car_id]
            cursor.execute(sql, values)
            conn.commit()
            print("Car updated successfully!")
            return True
        except mysql.connector.Error as err:
            print(f"Error updating car: {err}")
            return False
        finally:
            conn.close()

def list_available_cars():
    """List all available cars"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cars WHERE status = 'available'")
            cars = cursor.fetchall()
            return cars
        finally:
            conn.close()

# Booking Management Functions
def create_booking(customer_id, car_id, start_date, end_date, pickup_location, dropoff_location, total_amount, payment_method):
    """Create a new booking"""
    conn = get_db_connection()
    if not conn:
        raise Exception("Could not connect to database")
    
    try:
        cursor = conn.cursor()
        sql = """INSERT INTO bookings 
                (customer_id, car_id, start_date, end_date, pickup_location, dropoff_location, 
                 total_amount, status, payment_status, payment_method) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', 'pending', %s)"""
        cursor.execute(sql, (customer_id, car_id, start_date, end_date, 
                           pickup_location, dropoff_location, total_amount, payment_method))
        
        conn.commit()
        booking_id = cursor.lastrowid
        return booking_id
    except mysql.connector.Error as err:
        conn.rollback()
        raise Exception(f"Database error: {str(err)}")
    finally:
        conn.close()

def update_booking_status(booking_id, status):
    """Update booking status and car availability"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Start transaction
            conn.start_transaction()
            
            # Update booking status
            cursor.execute("UPDATE bookings SET status = %s WHERE booking_id = %s", 
                         (status, booking_id))
            
            # If approved, update car status to 'rented'
            if status == 'approved':
                cursor.execute("""
                    UPDATE cars c
                    JOIN bookings b ON c.car_id = b.car_id
                    SET c.status = 'rented'
                    WHERE b.booking_id = %s
                """, (booking_id,))
            
            # If rejected, ensure car remains/returns to 'available'
            elif status == 'rejected':
                cursor.execute("""
                    UPDATE cars c
                    JOIN bookings b ON c.car_id = b.car_id
                    SET c.status = 'available'
                    WHERE b.booking_id = %s
                """, (booking_id,))
            
            # Commit transaction
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error updating booking: {err}")
            conn.rollback()
            return False
        finally:
            conn.close()
    return False

def list_user_bookings(user_id):
    """List bookings for a specific user"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT b.*, c.brand, c.model 
                FROM bookings b 
                JOIN cars c ON b.car_id = c.car_id 
                WHERE b.customer_id = %s
                """, (user_id,))
            bookings = cursor.fetchall()
            return bookings
        finally:
            conn.close()

# Payment Functions
def record_payment(booking_id, amount):
    """Record a payment for a booking"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO payments (booking_id, amount) VALUES (%s, %s)", 
                         (booking_id, amount))
            cursor.execute("UPDATE bookings SET payment_status = 'paid' WHERE booking_id = %s", 
                         (booking_id,))
            conn.commit()
            print("Payment recorded successfully!")
            return True
        except mysql.connector.Error as err:
            print(f"Error recording payment: {err}")
            return False
        finally:
            conn.close()

def get_payment_history(booking_id=None):
    """Get payment history, optionally filtered by booking_id"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            if booking_id:
                cursor.execute("SELECT * FROM payments WHERE booking_id = %s", (booking_id,))
            else:
                cursor.execute("SELECT * FROM payments")
            payments = cursor.fetchall()
            return payments
        finally:
            conn.close()

# Maintenance Functions
def log_maintenance(car_id, description):
    """Log a maintenance record for a car"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO maintenance (car_id, description) VALUES (%s, %s)", 
                         (car_id, description))
            conn.commit()
            print("Maintenance record logged successfully!")
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error logging maintenance: {err}")
            return None
        finally:
            conn.close()

def create_maintenance_record(car_id, description):
    """Create a maintenance record for a car"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Start transaction
            conn.start_transaction()
            
            # Update car status
            cursor.execute("UPDATE cars SET status = 'maintenance' WHERE car_id = %s", 
                         (car_id,))
            
            # Create maintenance record
            cursor.execute("""
                INSERT INTO maintenance (car_id, description, date_created)
                VALUES (%s, %s, NOW())
            """, (car_id, description))
            
            conn.commit()
            return True
        except mysql.connector.Error as err:
            conn.rollback()
            print(f"Error creating maintenance record: {err}")
            return False
        finally:
            conn.close()
    return False

def list_maintenance_records(car_id=None):
    """List maintenance records, optionally filtered by car_id"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            if car_id:
                cursor.execute("""
                    SELECT m.*, c.brand, c.model 
                    FROM maintenance m 
                    JOIN cars c ON m.car_id = c.car_id 
                    WHERE m.car_id = %s
                    """, (car_id,))
            else:
                cursor.execute("""
                    SELECT m.*, c.brand, c.model 
                    FROM maintenance m 
                    JOIN cars c ON m.car_id = c.car_id
                    """)
            records = cursor.fetchall()
            return records
        finally:
            conn.close()

def get_booking_details(booking_id):
    """Get complete booking details including customer and car information"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    b.*, 
                    u.full_name, u.email, u.phone, u.license_no,
                    c.brand, c.model, c.plate_no, c.color, c.rate_per_day
                FROM bookings b
                JOIN users u ON b.customer_id = u.user_id
                JOIN cars c ON b.car_id = c.car_id
                WHERE b.booking_id = %s
            """
            cursor.execute(sql, (booking_id,))
            return cursor.fetchone()
        finally:
            conn.close()
    return None
