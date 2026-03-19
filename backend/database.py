import sqlite3
import os

def get_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Points to hotel.db in the XYZ folder
    db_path = os.path.join(base_dir, "../hotel.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn