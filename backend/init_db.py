import sqlite3
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
default_db_path = os.path.join(base_dir, "hotel.db")

def init_db(db_path=None):
    target_db = db_path if db_path else default_db_path
    if os.path.exists(target_db):
        os.remove(target_db)

    conn = sqlite3.connect(target_db)
    cur = conn.cursor()

    # 1. Create rooms table
    cur.execute("""
    CREATE TABLE rooms(
        id INTEGER PRIMARY KEY,
        number TEXT,
        type TEXT,
        base_price INTEGER,
        current_price INTEGER,
        status TEXT,
        image TEXT,
        amenities TEXT,
        rating REAL
    )
    """)

    # 2. Create guests table
    cur.execute("""
    CREATE TABLE guests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT UNIQUE,
        loyalty_points INTEGER DEFAULT 0
    )
    """)

    # 3. Create reservations table
    cur.execute("""
    CREATE TABLE reservations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_id INTEGER,
        room_id INTEGER,
        check_in DATE,
        check_out DATE,
        status TEXT,
        total_amount REAL,
        payment_status TEXT
    )
    """)

    # 4. Create users table for login and roles
    cur.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT, guest_id INTEGER NULL)")
    
    # 5. Create food orders table
    cur.execute("""
    CREATE TABLE food_orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT,
        guest_name TEXT,
        items TEXT,
        total_price INTEGER,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 6. Cleaning Logs
    cur.execute("""
    CREATE TABLE cleaning_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT NOT NULL,
        staff_name TEXT NOT NULL,
        cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 7. Maintenance Tickets
    cur.execute("""
    CREATE TABLE maintenance_tickets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT NOT NULL,
        reported_by TEXT NOT NULL,
        issue_desc TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Insert sample users
    cur.execute("INSERT INTO users VALUES (1, 'admin', 'admin', 'admin', NULL)")
    cur.execute("INSERT INTO users VALUES (2, 'guest1', 'pass', 'guest', 1)")
    cur.execute("INSERT INTO users VALUES (3, 'staff1', 'pass', 'staff', NULL)")

    # Insert sample guest
    cur.execute("INSERT INTO guests (id, name, phone, email, loyalty_points) VALUES (1, 'John Doe', '1234567890', 'john@example.com', 500)")

    # Insert room data
    import random
    
    rooms_data = []
    r_id = 1
    
    # 1st Floor: Deluxe Room (101 - 110)
    for i in range(1, 11):
        num = f"1{i:02d}"
        status = 'AVAILABLE'
        rooms_data.append((r_id, num, 'Deluxe Room', 5000, 5000, status, 'https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=800&q=80', 'WiFi, AC, Smart TV', 4.5))
        r_id += 1
        
    # 2nd Floor: Executive Suite (201 - 210)
    for i in range(1, 11):
        num = f"2{i:02d}"
        status = 'AVAILABLE'
        rooms_data.append((r_id, num, 'Executive Suite', 8000, 8500, status, 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=800&q=80', 'WiFi, AC, Work Desk, Lounge Area', 4.7))
        r_id += 1
        
    # 3rd Floor: Presidential Suite (301 - 310)
    for i in range(1, 11):
        num = f"3{i:02d}"
        # Presidential suites are usually very available and pristine
        status = 'AVAILABLE'
        rooms_data.append((r_id, num, 'Presidential Suite', 12000, 14000, status, 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?auto=format&fit=crop&w=800&q=80', 'WiFi, AC, Jacuzzi, Butler Service, Mini-bar', 4.9))
        r_id += 1

    cur.executemany("INSERT INTO rooms VALUES (?,?,?,?,?,?,?,?,?)", rooms_data)
    
    # No dummy reservations for a completely fresh start

    conn.commit()
    conn.close()
    print("DONE: Database recreated with new schema and mock data for UI showcasing!")

if __name__ == "__main__":
    init_db()