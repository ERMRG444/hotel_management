import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables (Root passwords/paths if needed)
load_dotenv()

def init_database():
    # Using your default local database file
    db_path = os.getenv('DB_PATH', 'hotel.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print(f"Connected to database at: {db_path}")

    # --- 1. ADMIN & BOOKING SERVICE TABLES ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'AVAILABLE'
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_id INTEGER,
            room_id INTEGER,
            status TEXT DEFAULT 'ACTIVE',
            FOREIGN KEY(guest_id) REFERENCES guests(id),
            FOREIGN KEY(room_id) REFERENCES rooms(id)
        )
    ''')

    # --- 2. FOOD SERVICE TABLE ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS food_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL,
            guest_name TEXT NOT NULL,
            items TEXT NOT NULL,
            total_price REAL,
            status TEXT DEFAULT 'PREPARING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- 3. HOUSEKEEPING SERVICE TABLE ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cleaning_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL,
            staff_name TEXT NOT NULL,
            cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- 4. MAINTENANCE SERVICE TABLE ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS maintenance_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL,
            reported_by TEXT NOT NULL,
            issue_desc TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ All 3 Service tables verified/created successfully.")

if __name__ == "__main__":
    init_database()