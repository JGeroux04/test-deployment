import numpy as np

def test_login_face_success(client, mocker):
    mock_get_collection = mocker.patch('routes.login_face.get_users_collection')
    mock_collection = mock_get_collection.return_value
    mock_collection.find.return_value = [{
        "username": "testuser",
        "profile_picture": "data:image/jpeg;base64,<placeholder>"
    }]

    mocker.patch('routes.login_face.DeepFace.verify', return_value={"verified": True})

    mocker.patch('routes.login_face.base64.b64decode', return_value=b"fake_bytes")
    mocker.patch('routes.login_face.cv2.imdecode', return_value=np.zeros((100, 100, 3), dtype=np.uint8))

    fake_image = "data:image/jpeg;base64,<placeholder>"

    response = client.post('/api/login_face', json={"image": fake_image})

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Face recognized successfully!"
    assert "username" in data