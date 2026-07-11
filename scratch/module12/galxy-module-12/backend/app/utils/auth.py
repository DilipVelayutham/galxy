import functools
import os
import jwt
from flask import request, jsonify, current_app

def require_admin(f):
    """
    Decorator that checks for an Admin token in the Authorization header.
    Returns 401/403 if missing, invalid, or lacking admin role.
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return '', 200
            
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'success': False,
                'message': 'Authorization header is missing or empty.'
            }), 401
            
        # Parse Bearer <token>
        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                'success': False,
                'message': 'Invalid token format. Must be Bearer <token>.'
            }), 401
            
        token = parts[1]
        
        secret = current_app.config.get('JWT_SECRET') or os.environ.get('JWT_SECRET')
        if not secret:
            raise RuntimeError(
                'JWT_SECRET is not configured. Refusing to start with no admin secret.'
            )
            
        try:
            decoded = jwt.decode(token, secret, algorithms=["HS256"])
            if decoded.get("role") != "admin":
                return jsonify({
                    'success': False,
                    'message': 'Unauthorized request. Admin privileges required.'
                }), 403
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token has expired.'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token.'
            }), 401
            
        return f(*args, **kwargs)
    return decorated
