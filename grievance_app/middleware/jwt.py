
import requests
from flask import jsonify, g
import jwt
import os
from utils.user import get_user_by_id

JWT_SECRET = os.getenv('PUBLIC_KEY')  # Public key to verify JWT token


def verify_jwt(func):
    def wrapper(*args, **kwargs):
        auth_header = requests.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header missing'}), 401

        try:
            token = auth_header.split(" ")[1]
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=['RS256'])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return jsonify({'error': 'Invalid token'}), 401

            user = get_user_by_id(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            return func(decoded_token, *args, **kwargs)
        
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
    
    return wrapper
