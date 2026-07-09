from functools import wraps
import jwt
from flask import request, jsonify, g
from app.configs.env_config import Config
from bson import ObjectId

def decode_token(token):
    """Decodes a JWT token using the configured secret."""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired."}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token."}

def token_required(f):
    """Decorator to require a valid JWT token in Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
                
        if not token:
            return jsonify({
                "success": False,
                "message": "Authorization token is missing.",
                "errors": {}
            }), 401
            
        payload = decode_token(token)
        if "error" in payload:
            return jsonify({
                "success": False,
                "message": payload["error"],
                "errors": {}
            }), 401
            
        # Store user info in flask g context
        g.user_id = payload.get("user_id")
        g.role = payload.get("role", "customer") # Default to customer role
        g.user_name = payload.get("name")
        g.email = payload.get("email")
        
        return f(*args, **kwargs)
    return decorated

def role_required(allowed_roles):
    """Decorator to restrict access based on roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, "role") or g.role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "message": "Access denied. Insufficient permissions.",
                    "errors": {}
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def to_bson_id(val):
    """Safely converts a string value to a BSON ObjectId if valid."""
    if isinstance(val, str) and ObjectId.is_valid(val):
        return ObjectId(val)
    return val
