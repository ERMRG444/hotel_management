from flask import Blueprint, jsonify, request
from database import get_db
import random

room_bp = Blueprint("rooms", __name__)

@room_bp.route("/rooms", methods=["GET"])
def get_rooms():
    conn = get_db()
    cur = conn.cursor()
    
    # Auto-checkout logic for past reservations
    import datetime
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    cur.execute("""
        SELECT reservations.room_id, reservations.id as res_id, rooms.number as room_number 
        FROM reservations 
        JOIN rooms ON reservations.room_id = rooms.id
        WHERE check_out < ? AND reservations.status IN ('ACTIVE', 'CONFIRMED')
    """, (today_str,))
    past_reservations = cur.fetchall()
    
    if past_reservations:
        for res in past_reservations:
            room_id = res['room_id']
            res_id = res['res_id']
            room_number = res['room_number']
            
            # Mark reservation as COMPLETED
            cur.execute("UPDATE reservations SET status='COMPLETED' WHERE id=?", (res_id,))
            
            # Mark room as DIRTY
            cur.execute("UPDATE rooms SET status='DIRTY' WHERE id=?", (room_id,))
            
            # Add to cleaning logs
            cur.execute("INSERT INTO cleaning_logs (room_number, staff_name) VALUES (?, ?)", (room_number, "Auto-Dispatch (Past Checkout)"))
            
        conn.commit()

    cur.execute("SELECT * FROM rooms")
    rooms = [dict(row) for row in cur.fetchall()]
    conn.close()

    # Consistent pricing without fluctuation
    for r in rooms:
        if r['status'] == 'AVAILABLE':
            r['current_price'] = r['base_price']

    return jsonify(rooms)

@room_bp.route("/checkout/<int:room_id>", methods=["POST"])
def checkout_room(room_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE rooms SET status='DIRTY' WHERE id=?", (room_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Room checked out and marked DIRTY for housekeeping"})

@room_bp.route("/request_cleaning", methods=["POST"])
def request_cleaning():
    data = request.json
    room_number = data.get("room_number")
    
    if not room_number:
        return jsonify({"error": "Room number required"}), 400
        
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE rooms SET status='DIRTY' WHERE number=?", (room_number,))
    
    cur.execute("INSERT INTO cleaning_logs (room_number, staff_name) VALUES (?, ?)", (room_number, "Pending Auto-Assignment"))
    conn.commit()
    conn.close()
    
    return jsonify({"message": f"Housekeeping dispatched successfully to Room {room_number}!"})

@room_bp.route("/api/staff/checkout_room", methods=["POST"])
def staff_checkout_room():
    data = request.json
    room_number = data.get("room_number")
    
    if not room_number:
        return jsonify({"success": False, "message": "Room number required"}), 400
        
    conn = get_db()
    cur = conn.cursor()
    
    # Get room ID and status
    cur.execute("SELECT id, status FROM rooms WHERE number=?", (room_number,))
    room = cur.fetchone()
    if not room:
        conn.close()
        return jsonify({"success": False, "message": "Room not found"}), 404
        
    if room['status'] != 'OCCUPIED':
        conn.close()
        return jsonify({"success": False, "message": f"Room {room_number} is not currently occupied/booked."}), 400
        
    # Mark reservation as COMPLETED
    cur.execute("UPDATE reservations SET status='COMPLETED' WHERE room_id=? AND status IN ('CONFIRMED', 'ACTIVE')", (room['id'],))
    
    # Mark room as DIRTY
    cur.execute("UPDATE rooms SET status='DIRTY' WHERE id=?", (room['id'],))
    
    # Dispatch housekeeping automatically
    cur.execute("INSERT INTO cleaning_logs (room_number, staff_name) VALUES (?, ?)", (room_number, "Auto-Dispatch (Checkout)"))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": f"Room {room_number} checked out. Housekeeping notified."})


@room_bp.route("/api/staff/manual_checkin", methods=["POST"])
def staff_manual_checkin():
    data = request.json
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    mobile = data.get("mobile", "").strip()
    room_number = data.get("room_number", "").strip()
    check_in = data.get("check_in", "").strip()
    check_out = data.get("check_out", "").strip()
    
    if not all([first_name, last_name, mobile, room_number, check_in, check_out]):
        return jsonify({"success": False, "message": "All fields are required"}), 400
        
    conn = get_db()
    cur = conn.cursor()
    
    # 1. Verify Room Availability
    cur.execute("SELECT id, status, base_price FROM rooms WHERE number=?", (room_number,))
    room = cur.fetchone()
    if not room:
        return jsonify({"success": False, "message": "Room not found"}), 404
    if room["status"] != "AVAILABLE":
        return jsonify({"success": False, "message": f"Room is currently {room['status']}"}), 400
        
    full_name = f"{first_name} {last_name}"
    
    # 2. Get or Create Guest
    cur.execute("SELECT id FROM guests WHERE phone=?", (mobile,))
    guest = cur.fetchone()
    
    if not guest:
        cur.execute(
            "INSERT INTO guests(name, phone, email, loyalty_points) VALUES (?,?,?,?)",
            (full_name, mobile, f"{first_name.lower()}@example.com", 10)
        )
        guest_id = cur.lastrowid
    else:
        guest_id = guest["id"]
        cur.execute("UPDATE guests SET name=? WHERE id=?", (full_name, guest_id))

    # 3. Create or Update User Credentials for this guest
    username = f"{first_name}{last_name}".lower()
    password = mobile
    cur.execute("SELECT id FROM users WHERE username=?", (username,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users(username, password, role, guest_id) VALUES (?,?,?,?)",
                    (username, password, "guest", guest_id))
    else:
        cur.execute("UPDATE users SET password=?, guest_id=? WHERE username=?", (password, guest_id, username))
        
    # 4. Create Reservation
    from datetime import datetime
    try:
        in_date = datetime.strptime(check_in, "%Y-%m-%d")
        out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (out_date - in_date).days
        if nights < 1: nights = 1
    except:
        return jsonify({"success": False, "message": "Invalid date format"}), 400
        
    total_amount = nights * room["base_price"]
    
    cur.execute(
        "INSERT INTO reservations(guest_id, room_id, check_in, check_out, status, total_amount, payment_status) VALUES (?,?,?,?,?,?,?)",
        (guest_id, room["id"], check_in, check_out, "ACTIVE", total_amount, "PAID")
    )
    
    # 5. Set Room to Occupied
    cur.execute("UPDATE rooms SET status='OCCUPIED' WHERE id=?", (room["id"],))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True, 
        "message": f"Guest checked into Room {room_number}.",
        "credentials": {"username": username, "password": password}
    })