import sqlite3
import os
from flask import current_app

def get_db():
    try:
        if current_app and 'DATABASE_PATH' in current_app.config:
            db_path = current_app.config['DATABASE_PATH']
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
    except Exception:
        pass
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Points to hotel.db in the backend folder
    db_path = os.path.join(base_dir, "hotel.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn