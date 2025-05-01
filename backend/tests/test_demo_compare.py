import numpy as np

def test_demo_compare_success(client, mocker):
    mocker.patch('routes.demo_compare.DeepFace.verify', return_value={
        "verified": True,
        "distance": 0.3,
        "model_score": 99.2
    })

    dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
    mocker.patch('routes.demo_compare.base64.b64decode', return_value=b"fake_bytes")
    mocker.patch('routes.demo_compare.cv2.imdecode', return_value=dummy_image)

    dummy_base64 = "data:image/jpeg;base64,<fake_base64>"

    response = client.post('/api/demo_compare', json={
        "image1": dummy_base64,
        "image2": dummy_base64
    })

    assert response.status_code == 200
    data = response.json
    assert data["verified"] is True
    assert "similarity" in data
    assert "confidence" in data
    assert "base64_sample_img1" in data
    assert "array_sample_img1" in data