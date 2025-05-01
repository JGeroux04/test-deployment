from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db.mongo import get_users_collection

register_blueprint = Blueprint('register', __name__)

@register_blueprint.route('/register', methods=['POST'])
def register():
    users_collection = get_users_collection()  

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    profile_picture = data.get('profile_picture')  # Optional

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    if users_collection.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 409

    password_hash = generate_password_hash(password)

    user_data = {
        "username": username,
        "password_hash": password_hash,
    }

    if profile_picture:
        user_data['profile_picture'] = profile_picture

    users_collection.insert_one(user_data)

    return jsonify({"message": "User registered successfully"}), 201

@register_blueprint.route('/login', methods=['POST'])
def login():
    users_collection = get_users_collection() 

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = users_collection.find_one({"username": username})

    if not user:
        return jsonify({"error": "Invalid username or password"}), 401
    
    stored_password_hash = user.get('password_hash')

    if not stored_password_hash:
        return jsonify({"error": "Invalid username or password"}), 401
    
    if not check_password_hash(stored_password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful"}), 200