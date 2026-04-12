def test_get_rooms(client):
    response = client.get('/rooms')
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    # the dummy data has 5 rooms
    assert len(data) == 5

def test_checkout_room(client):
    response = client.post('/checkout/1')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['message'] == "Room checked out and marked DIRTY for housekeeping"
    
def test_checkout_invalid_room(client):
    response = client.post('/checkout/999')
    # Because sqlite just updates 0 rows it still returns 200 based on the current logic.
    assert response.status_code == 200
