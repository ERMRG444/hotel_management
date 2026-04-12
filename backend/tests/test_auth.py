def test_login_success(client):
    response = client.post('/login', json={
        "username": "admin",
        "password": "admin"
    })
    
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == "login success"
    assert data['role'] == "admin"
    assert data['username'] == "admin"

def test_login_invalid_credentials(client):
    response = client.post('/login', json={
        "username": "admin",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    
    data = response.get_json()
    assert data['message'] == "invalid credentials"
