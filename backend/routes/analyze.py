from flask import Blueprint, request, jsonify
import base64
import cv2
import numpy as np
from deepface import DeepFace

analyze_blueprint = Blueprint('analyze',__name__)

@analyze_blueprint.route('/analyze', methods=['POST'])
def analyze_face():
    if not request.json or 'image' not in request.json:
        return jsonify({"error": "Missing image data"}), 400

    image_data = request.json['image']
    try:
        header, encoded = image_data.split(',', 1)
        decoded_image = base64.b64decode(encoded)
        np_arr = np.frombuffer(decoded_image, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode image")

    except Exception as e:
        return jsonify({"error": f"Error decoding image: {e}"}), 400

    try:
        result = DeepFace.analyze(img, actions=['age', 'gender', 'race'], enforce_detection=False)

        if isinstance(result, list) and len(result) > 0:
            analysis = result[0]
        else:
            analysis = result

        return jsonify({
            "age": int(analysis.get('age', -1)),
            "gender": analysis.get('dominant_gender', 'Unknown'),
            "race": analysis.get('dominant_race', 'Unknown')
        })

    except Exception as e:
        return jsonify({"error": f"Analysis error: {e}"}), 500