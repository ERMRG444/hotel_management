from flask import Blueprint, request, jsonify
from database import get_db
from datetime import datetime

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/book", methods=["POST"])
def book_room():
    data = request.json
    name = data["name"]
    phone = data["phone"]
    email = data.get("email", f"{name.replace(' ', '').lower()}@example.com")
    room_id = data["room_id"]
    today_str = datetime.now().strftime("%Y-%m-%d")
    check_in = data.get("check_in", today_str)
    
    if check_in < today_str:
        return jsonify({"error": "Cannot book for a past date"}), 400

    if "check_out" not in data or not data["check_out"]:
        from datetime import timedelta
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out = (check_in_date + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        check_out = data["check_out"]
    total = data.get("total_amount", 0)

    conn = get_db()
    cur = conn.cursor()

    # Create Guest if not exists
    cur.execute("SELECT id FROM guests WHERE phone=?", (phone,))
    guest = cur.fetchone()
    
    if not guest:
        cur.execute(
            "INSERT INTO guests(name,phone,email,loyalty_points) VALUES (?,?,?,?)",
            (name, phone, email, 100)
        )
        guest_id = cur.lastrowid
    else:
        guest_id = guest["id"]
        # Add loyalty and update name
        cur.execute("UPDATE guests SET loyalty_points = loyalty_points + 50, name=? WHERE id=?", (name, guest_id))

    # Create Reservation
    cur.execute(
        "INSERT INTO reservations(guest_id,room_id,check_in,check_out,status,total_amount,payment_status) VALUES (?,?,?,?,?,?,?)",
        (guest_id, room_id, check_in, check_out, "CONFIRMED", total, "PAID")
    )

    cur.execute(
        "UPDATE rooms SET status='OCCUPIED' WHERE id=?",
        (room_id,)
    )

    # 4. Create User Account automatically
    username = name.replace(' ', '').lower()
    password = phone
    
    cur.execute("SELECT id FROM users WHERE username=?", (username,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users(username, password, role, guest_id) VALUES (?,?,?,?)",
                    (username, password, "guest", guest_id))
    else:
        cur.execute("UPDATE users SET password=?, guest_id=? WHERE username=?", (password, guest_id, username))

    conn.commit()
    return jsonify({
        "message": "Room successfully booked! You earned loyalty points.",
        "username": username,
        "password": password
    })

@booking_bp.route("/guest/details", methods=["GET"])
def get_guest_details():
    username = request.args.get("username")
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT guest_id FROM users WHERE username=?", (username,))
    user = cur.fetchone()
    
    if not user or not user["guest_id"]:
        return jsonify({"error": "Guest not found"}), 404
        
    guest_id = user["guest_id"]
    
    cur.execute("""
        SELECT rooms.number, rooms.type, reservations.check_in, reservations.check_out
        FROM reservations
        JOIN rooms ON reservations.room_id = rooms.id
        WHERE reservations.guest_id = ? AND reservations.status IN ('CONFIRMED', 'ACTIVE')
        ORDER BY reservations.id DESC LIMIT 1
    """, (guest_id,))
    
    room_info = cur.fetchone()
    if room_info:
        return jsonify(dict(room_info))
    return jsonify({"error": "No active rooms found"}), 404


@booking_bp.route("/order_food", methods=["POST"])
def order_food():
    data = request.json
    name = data.get("name")
    phone = data.get("phone")
    items = str(data.get("items")) 
    total = data.get("total")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT rooms.number 
        FROM guests 
        JOIN reservations ON guests.id = reservations.guest_id 
        JOIN rooms ON reservations.room_id = rooms.id 
        WHERE guests.phone = ? AND guests.name = ?
        AND reservations.status IN ('CONFIRMED', 'ACTIVE')
    """, (phone, name))
    
    result = cur.fetchone()
    
    if not result:
        return jsonify({"error": "No active room booking found for this Name and Phone Number!"}), 400
        
    room_number = result[0]

    cur.execute(
        "INSERT INTO food_orders(room_number, guest_name, items, total_price, status) VALUES (?,?,?,?,?)",
        (room_number, name, items, total, "PREPARING")
    )

    conn.commit()
    return jsonify({"message": "Food/Service order saved successfully!", "room": room_number})