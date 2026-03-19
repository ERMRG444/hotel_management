# Run this in a python shell or add to your app.py startup
import sqlite3
conn = sqlite3.connect('hotel.db')
conn.execute('CREATE TABLE IF NOT EXISTS food_orders (id INTEGER PRIMARY KEY, room_number TEXT, guest_name TEXT, items TEXT, total_price REAL, status TEXT)')
conn.close()

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

# These must be in the same folder as app.py
from auth_routes import auth_bp
from room_routes import room_bp
from booking_routes import booking_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(room_bp)
app.register_blueprint(booking_bp)

# --- NEW HOUSEKEEPING ROUTE ---
@app.route('/api/log_cleaning', methods=['POST'])
def log_cleaning():
    data = request.json
    staff_name = data.get('staff_name')
    room_number = data.get('room_number')

    if not staff_name or not room_number:
        return jsonify({"error": "Staff name and room number are required!"}), 400

    try:
        # Connect to database
        conn = sqlite3.connect('hotel.db')
        cur = conn.cursor()
        
        # Safety net: Create the cleaning_logs table if it doesn't exist yet!
        cur.execute('''
            CREATE TABLE IF NOT EXISTS cleaning_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT NOT NULL,
                staff_name TEXT NOT NULL,
                cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Save the log
        cur.execute("INSERT INTO cleaning_logs (room_number, staff_name) VALUES (?, ?)", (room_number, staff_name))
        conn.commit()
        conn.close()
        
        return jsonify({"message": f"Room {room_number} successfully marked as cleaned by {staff_name}!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ------------------------------

if __name__ == "__main__":
    # Make sure you run this from inside the backend folder
    app.run(debug=True, port=5000)