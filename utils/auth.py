from functools import wraps
from flask import request, jsonify, g

def login_required(f):
    """
    Decorator to mock authentication check.
    Looks for X-User-Id header. If not present, defaults to 'test_user_id' to simplify testing.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get("X-User-Id")
        if not user_id:
            # Fallback to test user for sandbox/testing purposes
            user_id = "test_user_id"
            
        g.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to mock administrator permission checks.
    Looks for X-Admin-Role header.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_role = request.headers.get("X-Admin-Role")
        user_id = request.headers.get("X-User-Id")
        
        # In test mode, allow if header is set or if we're simulating a test admin
        if admin_role == "super_admin" or user_id == "test_admin_id":
            g.user_id = user_id or "test_admin_id"
            g.admin_role = admin_role or "super_admin"
            return f(*args, **kwargs)
            
        # Return standard response contract for auth failure
        return jsonify({
            "success": False,
            "message": "Unauthorized access. Admin privileges required.",
            "errors": {"authorization": "Access denied."}
        }), 403
    return decorated_function
