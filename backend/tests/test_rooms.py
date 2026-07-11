def test_get_rooms(client):
    response = client.get('/rooms')
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    # the dummy data has 30 rooms
    assert len(data) == 30

def test_checkout_room(client):
    response = client.post('/checkout/1')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['message'] == "Room checked out and marked DIRTY for housekeeping"
    
def test_checkout_invalid_room(client):
    response = client.post('/checkout/999')
    # Because sqlite just updates 0 rows it still returns 200 based on the current logic.
    assert response.status_code == 200

def test_staff_checkout_unoccupied_room(client):
    response = client.post('/api/staff/checkout_room', json={"room_number": "101"})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert "is not currently occupied/booked." in data['message']

def test_staff_checkout_occupied_room(client, app):
    from database import get_db
    with app.app_context():
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE rooms SET status='OCCUPIED' WHERE number='101'")
        conn.commit()
        conn.close()

    response = client.post('/api/staff/checkout_room', json={"room_number": "101"})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert "checked out. Housekeeping notified." in data['message']

def test_staff_checkout_nonexistent_room(client):
    response = client.post('/api/staff/checkout_room', json={"room_number": "999"})
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert data['message'] == "Room not found"

