def test_log_cleaning_success(client):
    response = client.post('/api/log_cleaning', json={
        "staff_name": "John",
        "room_number": "101"
    })
    
    data = response.get_json()
    assert response.status_code == 200
    assert "successfully marked as cleaned" in data['message']
    
def test_log_cleaning_missing_data(client):
    response = client.post('/api/log_cleaning', json={
        "staff_name": "John"
    })
    
    data = response.get_json()
    assert response.status_code == 400
    assert data['error'] == "Staff name and room number are required!"
