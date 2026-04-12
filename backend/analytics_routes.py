from flask import Blueprint, jsonify
from database import get_db

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/dashboard_stats", methods=["GET"])
def get_stats():
    conn = get_db()
    cur = conn.cursor()

    # Total Occupancy
    cur.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM rooms WHERE status='OCCUPIED'")
    occupied_rooms = cur.fetchone()[0]

    # Total Revenue (sum of all PAID reservations) for current month
    import datetime
    current_month = datetime.datetime.now().strftime('%Y-%m')
    cur.execute("SELECT SUM(total_amount) FROM reservations WHERE payment_status='PAID' AND strftime('%Y-%m', check_in) = ?", (current_month,))
    sum_rev = cur.fetchone()[0]
    revenue = sum_rev if sum_rev else 0

    # Housekeeping Status
    cur.execute("SELECT COUNT(*) FROM rooms WHERE status='DIRTY'")
    dirty_rooms = cur.fetchone()[0]

    conn.close()
    
    occupancy_rate = round((occupied_rooms / max(total_rooms, 1)) * 100, 1)

    return jsonify({
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "occupancy_rate": occupancy_rate,
        "dirty_rooms": dirty_rooms,
        "total_revenue": revenue
    })

@analytics_bp.route("/recent_bookings", methods=["GET"])
def recent_bookings():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT reservations.id, guests.name, rooms.number, reservations.check_in, reservations.check_out, reservations.status
        FROM reservations
        JOIN guests ON guests.id = reservations.guest_id
        JOIN rooms ON rooms.id = reservations.room_id
        ORDER BY reservations.id DESC LIMIT 5
    """)
    bookings = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(bookings)

@analytics_bp.route("/api/admin/revenue_chart", methods=["GET"])
def get_revenue_chart():
    conn = get_db()
    cur = conn.cursor()
    # Fetch last 6 months of revenue data grouped by month
    cur.execute("""
        SELECT strftime('%Y-%m', check_in) as month, SUM(total_amount) 
        FROM reservations 
        WHERE payment_status='PAID' 
        GROUP BY month 
        ORDER BY month ASC
    """)
    rows = cur.fetchall()
    conn.close()

    import datetime
    import calendar
    
    # Generate last 6 months list to assure we have data points even for empty months
    labels = []
    data_points = []
    
    # Create a dictionary from the DB result for easy lookup
    revenue_dict = {row[0]: row[1] for row in rows if row[0]}
    
    now = datetime.datetime.now()
    for i in range(5, -1, -1):
        target_date = now.replace(day=1) - datetime.timedelta(days=30*i)
        # Handle tricky month math (timedelta 30 isn't perfect, but suitable here or subtract months)
        month_idx = (now.month - i - 1) % 12 + 1
        year_idx = now.year if month_idx <= now.month else now.year - 1
        
        target_month_str = f"{year_idx}-{month_idx:02d}"
        
        label = calendar.month_abbr[month_idx]
        if i == 0:
            label += " (Live)"
            
        labels.append(label)
        data_points.append(revenue_dict.get(target_month_str, 0))
    
    return jsonify({
        "labels": labels,
        "data": data_points
    })
