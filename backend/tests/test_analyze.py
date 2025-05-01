import numpy as np

def test_analyze_face(client, mocker):
    mocker.patch('routes.analyze.DeepFace.analyze', return_value=[{
        "age": 25,
        "dominant_gender": "Man",
        "dominant_race": "White"
    }])

    mocker.patch('routes.analyze.base64.b64decode', return_value=b"fake_bytes")
    mocker.patch('routes.analyze.cv2.imdecode', return_value=np.zeros((100, 100, 3), dtype=np.uint8))

    fake_image = "data:image/jpeg;base64,<placeholder>"

    response = client.post('/api/analyze', json={"image": fake_image})

    assert response.status_code == 200
    data = response.get_json()
    assert "age" in data
    assert "gender" in data
    assert "race" in data