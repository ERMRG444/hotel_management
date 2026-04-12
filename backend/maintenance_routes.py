from flask import Blueprint, request, jsonify
from database import get_db

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/api/staff/report_maintenance', methods=['POST'])
def report_maintenance():
    data = request.json
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO maintenance_tickets (room_number, reported_by, issue_desc) VALUES (?, ?, ?)",
        (data['room_number'], data['reported_by'], data['issue_desc'])
    )
    
    # Also mark room as MAINTENANCE
    cur.execute("UPDATE rooms SET status = 'MAINTENANCE' WHERE number = ?", (data['room_number'],))
    
    db.commit()
    db.close()
    return jsonify({"success": True, "message": "Ticket created."})

@maintenance_bp.route('/api/staff/maintenance_tickets', methods=['GET'])
def get_tickets():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM maintenance_tickets WHERE status = 'PENDING' ORDER BY created_at DESC")
    tickets = [dict(row) for row in cur.fetchall()]
    db.close()
    return jsonify(tickets)

@maintenance_bp.route('/api/staff/resolve_maintenance', methods=['POST'])
def resolve_ticket():
    data = request.json
    db = get_db()
    cur = db.cursor()
    
    # Get room number before completing
    cur.execute("SELECT room_number FROM maintenance_tickets WHERE id = ?", (data['ticket_id'],))
    room = cur.fetchone()
    if not room:
        return jsonify({"success": False, "message": "Ticket not found"}), 404
        
    cur.execute("UPDATE maintenance_tickets SET status = 'RESOLVED' WHERE id = ?", (data['ticket_id'],))
    
    # Mark room back to AVAILABLE or maybe DIRTY
    # Since maintenance was in there, they'll need housekeeping, so mark it DIRTY
    cur.execute("UPDATE rooms SET status = 'DIRTY' WHERE number = ?", (room['room_number'],))
    
    db.commit()
    db.close()
    return jsonify({"success": True, "message": "Ticket resolved."})
