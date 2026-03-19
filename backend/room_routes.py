from flask import Blueprint, jsonify, request
from database import get_db

room_bp = Blueprint("rooms", __name__)

@room_bp.route("/rooms", methods=["GET"])
def get_rooms():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM rooms")
    # Convert rows to dictionaries so we can access r.image
    rooms = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rooms)

@room_bp.route("/checkout/<int:room_id>", methods=["POST"])
def checkout_room(room_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE rooms SET status='AVAILABLE' WHERE id=?", (room_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Success"})