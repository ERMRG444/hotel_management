import sqlite3
import os

# Find the XYZ folder
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "../hotel.db")

def init_db():
    # Force delete the old database to clear errors
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Create rooms table
    cur.execute("""
    CREATE TABLE rooms(
        id INTEGER PRIMARY KEY,
        number TEXT,
        type TEXT,
        price INTEGER,
        status TEXT,
        image TEXT
    )
    """)

    # 2. Create guests table (THIS WAS MISSING!)
    cur.execute("""
    CREATE TABLE guests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT
    )
    """)

    # 3. Create reservations table (THIS WAS MISSING!)
    cur.execute("""
    CREATE TABLE reservations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_id INTEGER,
        room_id INTEGER,
        status TEXT
    )
    """)

    # 4. Create users table for login
    cur.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cur.execute("INSERT INTO users VALUES (1, 'admin', 'admin')")

    # 5. Create food orders table
    cur.execute("""
    CREATE TABLE food_orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT,
        guest_name TEXT,
        items TEXT,
        total_price INTEGER,
        status TEXT
    )
    """)

    # Insert room data
    rooms_data = [
        (1, '101', 'Deluxe', 3000, 'AVAILABLE', 'https://images.pexels.com/photos/164595/pexels-photo-164595.jpeg?auto=compress&cs=tinysrgb&w=500'),
        (2, '102', 'Suite', 5000, 'AVAILABLE', 'https://images.pexels.com/photos/271618/pexels-photo-271618.jpeg?auto=compress&cs=tinysrgb&w=500'),
        (3, '103', 'Standard', 2000, 'AVAILABLE', 'https://images.pexels.com/photos/271624/pexels-photo-271624.jpeg?auto=compress&cs=tinysrgb&w=500')
    ]

    cur.executemany("INSERT INTO rooms VALUES (?,?,?,?,?,?)", rooms_data)
    
    conn.commit()
    conn.close()
    print("DONE: Database recreated with ALL missing tables and fresh images!")

if __name__ == "__main__":
    init_db()