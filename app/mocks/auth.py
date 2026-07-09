from functools import wraps
from flask import request, jsonify, g
from bson import ObjectId

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = request.headers.get("X-User-Id")
        if not user_id:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                user_id = auth_header.split(" ")[1]
        
        if not user_id:
            return jsonify({
                "success": False,
                "message": "Unauthorized: Authentication required"
            }), 401
            
        try:
            g.user_id = ObjectId(user_id)
            g.user = {"_id": g.user_id}
        except Exception:
            return jsonify({
                "success": False,
                "message": "Unauthorized: Invalid user ID format"
            }), 401
            
        return f(*args, **kwargs)
    return decorated
