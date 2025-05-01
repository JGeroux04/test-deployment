import uuid

def test_register(client, mocker):
    unique_username = f"user_{uuid.uuid4().hex[:8]}"

    mock_get_collection = mocker.patch('routes.register.get_users_collection')
    mock_collection = mock_get_collection.return_value
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value = None

    response = client.post('/api/register', json={
        "username": unique_username,
        "password": "password123",
        "profile_picture": "data:image/jpeg;base64,<placeholder>"
    })

    print("DEBUG response:", response.status_code, response.json)
    assert response.status_code == 201
    assert response.json['message'] == "User registered successfully"