from functools import wraps
from flask import request, jsonify

def auth_required(f):
    """
    Simulates token-based owner/admin authorization gating.
    Checks headers X-User-Id and X-User-Role.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = kwargs.get("user_id")
        req_user_id = request.headers.get("X-User-Id")
        req_role = request.headers.get("X-User-Role")
        
        # Admin bypasses owner restrictions
        if req_role == "admin":
            return f(*args, **kwargs)
            
        if not req_user_id:
            return jsonify({
                "success": False,
                "message": "Authentication required. X-User-Id header is missing."
            }), 401
            
        # Verify requested user_id matches X-User-Id header
        if user_id and str(req_user_id) != str(user_id):
            return jsonify({
                "success": False,
                "message": "Access denied. You do not have permission to view this resource."
            }), 403
            
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Simulates admin-only authorization gating."""
    @wraps(f)
    def decorated(*args, **kwargs):
        req_role = request.headers.get("X-User-Role")
        
        if req_role != "admin":
            return jsonify({
                "success": False,
                "message": "Access denied. Admin permissions are required."
            }), 403
            
        return f(*args, **kwargs)
    return decorated
