
import request
from flask import jsonify, g
import jwt
import os

JWT_SECRET = os.getenv('PUBLIC_KEY')  # Public key to verify JWT token


def verify_jwt(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header missing'}), 401

        try:
            token = auth_header.split(" ")[1]
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=['RS256'])
            user_id = decoded_token.get('user_id')
            g.user = decoded_token  # Save decoded token in global context
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return func(*args, **kwargs)
    return wrapper
