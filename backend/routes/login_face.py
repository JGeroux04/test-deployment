from flask import Blueprint, request, jsonify
import base64
import cv2
import numpy as np
from deepface import DeepFace
from db.mongo import get_users_collection

login_face_blueprint = Blueprint('login_face', __name__)

@login_face_blueprint.route('/login_face', methods=['POST'])
def login_face():
    users_collection = get_users_collection()

    if not request.json or 'image' not in request.json:
        return jsonify({"error": "Missing image data"}), 400

    image_data = request.json['image']

    try:
        header, encoded = image_data.split(',', 1)
        uploaded_img = base64.b64decode(encoded)
        uploaded_np = np.frombuffer(uploaded_img, np.uint8)
        img1 = cv2.imdecode(uploaded_np, cv2.IMREAD_COLOR)

        if img1 is None:
            raise ValueError("Could not decode uploaded image.")

    except Exception as e:
        return jsonify({"error": f"Error decoding uploaded image: {e}"}), 400

    try:
        users = users_collection.find({})
        for user in users:
            stored_profile = user.get('profile_picture')
            if not stored_profile:
                continue 

            try:
                header, encoded_stored = stored_profile.split(',', 1)
                stored_img = base64.b64decode(encoded_stored)
                stored_np = np.frombuffer(stored_img, np.uint8)
                img2 = cv2.imdecode(stored_np, cv2.IMREAD_COLOR)

                if img2 is None:
                    continue

                verification_result = DeepFace.verify(
                    img1_path = img1,
                    img2_path = img2,
                    enforce_detection=False
                )

                if verification_result.get("verified"):
                    return jsonify({
                        "message": "Face recognized successfully!",
                        "username": user["username"]
                    }), 200

            except Exception as e:
                print(f"Error verifying user {user.get('username')}: {e}")
                continue

        
        return jsonify({"error": "No matching face found."}), 401

    except Exception as e:
        return jsonify({"error": f"Verification error: {e}"}), 500
