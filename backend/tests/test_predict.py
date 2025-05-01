import numpy as np

def test_predict_emotion(client, mocker):
    mocker.patch('routes.predict.DeepFace.analyze', return_value=[{
        "dominant_emotion": "happy",
        "emotion": {"happy": 98.5},
        "region": {"x": 1, "y": 2, "w": 3, "h": 4}
    }])

    mocker.patch('routes.predict.base64.b64decode', return_value=b"fake_bytes")
    mocker.patch('routes.predict.cv2.imdecode', return_value=np.zeros((100, 100, 3), dtype=np.uint8))

    fake_image = "data:image/jpeg;base64,<placeholder>"
    response = client.post('/api/predict', json={"image": fake_image})

    assert response.status_code == 200
    data = response.get_json()
    assert data['emotion'] == "happy"
    assert isinstance(data['confidence'], float)
    assert "details" in data
    assert isinstance(data["region"], dict)
