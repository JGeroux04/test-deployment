from flask import Blueprint, request, jsonify
import base64
import numpy as np
import cv2
from deepface import DeepFace

demo_blueprint = Blueprint('demo', __name__)

@demo_blueprint.route('/demo_compare', methods=['POST'])
def demo_compare():
    data = request.json
    if not data or 'image1' not in data or 'image2' not in data:
        return jsonify({"error": "Both images are required"}), 400

    try:
        # Decode base64 strings
        header1, encoded1 = data['image1'].split(',', 1)
        header2, encoded2 = data['image2'].split(',', 1)

        decoded1 = base64.b64decode(encoded1)
        decoded2 = base64.b64decode(encoded2)

        img1 = cv2.imdecode(np.frombuffer(decoded1, np.uint8), cv2.IMREAD_COLOR)
        img2 = cv2.imdecode(np.frombuffer(decoded2, np.uint8), cv2.IMREAD_COLOR)

        if img1 is None or img2 is None:
            raise ValueError("Failed to decode one or both images.")

        result = DeepFace.verify(img1, img2, enforce_detection=False)

        return jsonify({
            "base64_sample_img1": encoded1[:100],
            "base64_sample_img2": encoded2[:100],
            "array_sample_img1": str(img1[0:2, 0:4].tolist()),
            "array_sample_img2": str(img2[0:2, 0:4].tolist()),
            "similarity": result.get("distance"),
            "verified": result.get("verified"),
            "confidence": result.get("model_score")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500