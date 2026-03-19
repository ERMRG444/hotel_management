from flask import Blueprint, request, jsonify
from database import get_db

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/book", methods=["POST"])
def book_room():

    data = request.json

    name = data["name"]
    phone = data["phone"]
    room_id = data["room_id"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO guests(name,phone) VALUES (?,?)",
        (name, phone)
    )

    guest_id = cur.lastrowid

    cur.execute(
        "INSERT INTO reservations(guest_id,room_id,status) VALUES (?,?,?)",
        (guest_id,room_id,"CONFIRMED")
    )

    cur.execute(
        "UPDATE rooms SET status='OCCUPIED' WHERE id=?",
        (room_id,)
    )

    conn.commit()

    return jsonify({"message":"room booked"})

@booking_bp.route("/order_food", methods=["POST"])
def order_food():
    data = request.json
    
    name = data.get("name")
    phone = data.get("phone")
    # THE ONLY FIX: SQLite needs a string, not a list
    items = str(data.get("items")) 
    total = data.get("total")

    conn = get_db()
    cur = conn.cursor()

    # Back to your original search logic
    cur.execute("""
        SELECT rooms.number 
        FROM guests 
        JOIN reservations ON guests.id = reservations.guest_id 
        JOIN rooms ON reservations.room_id = rooms.id 
        WHERE guests.phone = ? AND guests.name = ?
    """, (phone, name))
    
    result = cur.fetchone()
    
    if not result:
        return jsonify({"error": "No active room booking found for this Name and Phone Number!"}), 400
        
    room_number = result[0]

    # Saving exactly as you had it
    cur.execute(
        "INSERT INTO food_orders(room_number, guest_name, items, total_price, status) VALUES (?,?,?,?,?)",
        (room_number, name, items, total, "PREPARING")
    )

    conn.commit()
    return jsonify({"message": "Food order saved successfully!", "room": room_number})