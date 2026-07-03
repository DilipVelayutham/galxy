from flask import Blueprint, request, jsonify
from app.services.auth_service import forgot_password, reset_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/forgot-password', methods=['POST'])
def handle_forgot_password():
    """
    POST /api/auth/forgot-password
    Accepts: { "email" }
    Always returns 200 on valid email format (enumeration-safe)
    """
    data = request.get_json() or {}
    email = data.get('email')
    
    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required",
            "errors": {"email": "Email is required"}
        }), 400
        
    result = forgot_password(email)
    
    if not result["success"]:
        # If validator rejected it due to format issues
        return jsonify({
            "success": False,
            "message": result["message"],
            "errors": {"email": result["message"]}
        }), 400
        
    return jsonify({
        "success": True,
        "message": result["message"],
        "data": {}
    }), 200

@auth_bp.route('/reset-password', methods=['POST'])
def handle_reset_password():
    """
    POST /api/auth/reset-password
    Accepts: { "token", "new_password" }
    """
    data = request.get_json() or {}
    token = data.get('token')
    new_password = data.get('new_password')
    
    errors = {}
    if not token:
        errors["token"] = "Token is required"
    if not new_password:
        errors["new_password"] = "New password is required"
        
    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed",
            "errors": errors
        }), 400
        
    result = reset_password(token, new_password)
    
    if not result["success"]:
        return jsonify({
            "success": False,
            "message": result["message"],
            "errors": {"new_password": result["message"]}
        }), 400
        
    return jsonify({
        "success": True,
        "message": result["message"],
        "data": {}
    }), 200
