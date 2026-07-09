import jwt
from functools import wraps
from flask import request, jsonify, g
from app.config import Config

def decode_token(token):
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"success": False, "message": "Authorization header is missing"}), 401
        
        try:
            token_type, token = auth_header.split(" ")
            if token_type.lower() != "bearer":
                return jsonify({"success": False, "message": "Invalid token type, must be Bearer"}), 401
        except ValueError:
            return jsonify({"success": False, "message": "Invalid Authorization header format"}), 401
        
        decoded = decode_token(token)
        if "error" in decoded:
            return jsonify({"success": False, "message": decoded["error"]}), 401
        
        # Hydrate user info in request context
        g.user = {
            "id": decoded.get("user_id"),
            "email": decoded.get("email"),
            "role": decoded.get("role")
        }
        return f(*args, **kwargs)
    return decorated

def require_admin(f):
    @wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        if g.user.get("role") != "super_admin":
            return jsonify({"success": False, "message": "Forbidden: Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated
