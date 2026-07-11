import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db
from init_db import init_db

from auth_routes import auth_bp
from room_routes import room_bp
from booking_routes import booking_bp
from analytics_routes import analytics_bp
from maintenance_routes import maintenance_bp

# Ensure database is initialized
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hotel.db")
if not os.path.exists(db_path):
    print("Database not found! Initializing hotel.db...")
    try:
        init_db(db_path)
    except Exception as e:
        print(f"Error initializing database: {e}")

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

app.register_blueprint(auth_bp)
app.register_blueprint(room_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(maintenance_bp)

# --- HOUSEKEEPING ROUTE ---
@app.route('/api/log_cleaning', methods=['POST'])
def log_cleaning():
    data = request.json
    staff_name = data.get('staff_name')
    room_number = data.get('room_number')

    if not staff_name or not room_number:
        return jsonify({"error": "Staff name and room number are required!"}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("INSERT INTO cleaning_logs (room_number, staff_name) VALUES (?, ?)", (room_number, staff_name))
        
        # Check if room has an active booking
        cur.execute("""
            SELECT id FROM reservations 
            WHERE room_id = (SELECT id FROM rooms WHERE number = ?) 
            AND status IN ('CONFIRMED', 'ACTIVE')
        """, (room_number,))
        reservation = cur.fetchone()

        if reservation:
            new_status = 'OCCUPIED'
        else:
            new_status = 'AVAILABLE'

        cur.execute("UPDATE rooms SET status=? WHERE number=?", (new_status, room_number))
        
        conn.commit()

        conn.close()
        
        return jsonify({"message": f"Room {room_number} successfully marked as cleaned by {staff_name}!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ------------------------------

# --- GET LOGS ROUTES ---
@app.route('/api/logs/cleaning', methods=['GET'])
def get_cleaning_logs():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, room_number, staff_name, cleaned_at FROM cleaning_logs ORDER BY cleaned_at DESC LIMIT 10")
        logs = [{"id": r[0], "room_number": r[1], "staff_name": r[2], "cleaned_at": r[3]} for r in cur.fetchall()]
        conn.close()
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs/food', methods=['GET'])
def get_food_logs():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, room_number, guest_name, items, total_price, status, created_at FROM food_orders ORDER BY id DESC")
        logs = [{"id": r[0], "room_number": r[1], "guest_name": r[2], "items": r[3], "total_price": r[4], "status": r[5], "created_at": r[6]} for r in cur.fetchall()]
        conn.close()
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/guest/order_food', methods=['POST'])
def guest_order_food():
    data = request.json
    username = data.get('username')
    room_number = data.get('room_number')
    items = data.get('items')
    total = data.get('total')

    if not username or not room_number:
        return jsonify({"error": "Missing user or room context"}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO food_orders(room_number, guest_name, items, total_price, status) VALUES (?,?,?,?,?)",
            (room_number, username, str(items), total, "PREPARING")
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Order successfully placed!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/staff/food_orders', methods=['GET'])
def staff_food_orders():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM food_orders WHERE status='PREPARING' ORDER BY id ASC")
        orders = [dict(row) for row in cur.fetchall()]
        conn.close()
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/staff/food_deliver', methods=['POST'])
def staff_food_deliver():
    data = request.json
    order_id = data.get('order_id')
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE food_orders SET status='DELIVERED' WHERE id=?", (order_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Order marked delivered!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/live_feed', methods=['GET'])
def admin_live_feed():
    try:
        conn = get_db()
        cur = conn.cursor()
        # Combine newest bookings, cleaning logs, and food orders into a chronological feed
        feed = []
        
        cur.execute("SELECT id, guest_id, room_id, status FROM reservations ORDER BY id DESC LIMIT 5")
        for r in cur.fetchall():
            feed.append({"type": "BOOKING", "desc": f"New booking: Room {r['room_id']} status {r['status']}", "id": r['id']})
            
        cur.execute("SELECT room_number, staff_name, cleaned_at FROM cleaning_logs ORDER BY id DESC LIMIT 5")
        for c in cur.fetchall():
            feed.append({"type": "CLEANING", "desc": f"Room {c['room_number']} cleaned by {c['staff_name']}", "time": c['cleaned_at']})
            
        cur.execute("SELECT room_number, guest_name, total_price, status FROM food_orders ORDER BY id DESC LIMIT 5")
        for f in cur.fetchall():
            feed.append({"type": "DINING", "desc": f"Room {f['room_number']} ordered food (₹{f['total_price']}) - {f['status']}"})
            
        conn.close()
        return jsonify(feed), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)