from flask import Blueprint, request, jsonify
import base64
import cv2
import numpy as np
from deepface import DeepFace

predict_blueprint = Blueprint('predict', __name__)

@predict_blueprint.route('/predict', methods=['POST'])
def predict_emotion():
    try:
        print("Received request")

        if not request.is_json:
            print("Request is NOT JSON")
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()

        if 'image' not in data:
            print("Missing 'image' key in JSON")
            return jsonify({"error": "Missing image data"}), 400

        # Decode base64 image
        header, encoded = data['image'].split(",", 1)
        decoded = base64.b64decode(encoded)
        np_arr = np.frombuffer(decoded, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            print("OpenCV failed to decode image")
            return jsonify({"error": "Invalid image"}), 400

        
        print("Running DeepFace.analyze...")
        result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)

        # Check for no face detected
        if isinstance(result, list) and len(result) == 0:
            return jsonify({"error": "No face detected"}), 200
        if isinstance(result, dict) and 'dominant_emotion' not in result:
            return jsonify({"error": "No face detected"}), 200

        # Handle DeepFace output
        if isinstance(result, list) and len(result) > 0:
            analysis = result[0]
        else:
            analysis = result

        dominant_emotion = analysis.get('dominant_emotion', 'N/A')
        confidence = analysis.get('emotion', {}).get(dominant_emotion, 0)

        
        if not isinstance(confidence, (int, float)):
            confidence = float(confidence)

       
        raw_details = analysis.get('emotion', {})
        details = {emotion: float(score) for emotion, score in raw_details.items()} if raw_details else {}

        
        raw_region = analysis.get('region', {})
        region = {}
        if raw_region:
            for k, v in raw_region.items():
                if v is None:
                    region[k] = None
                else:
                    if isinstance(v, tuple):
                        v = v[0]
                    region[k] = int(v)

        return jsonify({
            "emotion": dominant_emotion,
            "confidence": confidence,
            "details": details,
            "region": region
        })

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify({"error": str(e)}), 500