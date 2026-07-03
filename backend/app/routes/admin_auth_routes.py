import os
from flask import Blueprint, request, jsonify, make_response
from app.utils.auth_middleware import require_admin
from app.models.admin_user import AdminUser
from app.utils.token_helper import generate_access_token, generate_refresh_token
from app.utils.password_helper import verify_password
from app.db import get_db

admin_auth_bp = Blueprint('admin_auth', __name__)

COOKIE_NAME = 'admin_refresh_token'

def _set_refresh_cookie(response, refresh_token):
    is_prod = os.getenv("FLASK_ENV", "development") == "production"
    response.set_cookie(
        key=COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=is_prod,
        samesite='Lax',
        max_age=30 * 24 * 60 * 60,
        path='/api/admin/auth'
    )

def _clear_refresh_cookie(response):
    is_prod = os.getenv("FLASK_ENV", "development") == "production"
    response.delete_cookie(
        key=COOKIE_NAME,
        path='/api/admin/auth',
        secure=is_prod,
        samesite='Lax'
    )

@admin_auth_bp.route('/login', methods=['POST'])
def login():
    # In4 (Arun) will implement the full DB query / authentication logic.
    # Here is a basic working implementation for admin login to show how it reuses token_helper.
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400
        
    # Rate limiting on IP + Email combo
    ip_addr = request.remote_addr or "unknown_ip"
    rate_key = f"{ip_addr}+{email.strip().lower()}"
    from app.utils.rate_limiter import admin_login_limiter
    if admin_login_limiter.is_rate_limited(rate_key):
        return jsonify({
            "success": False,
            "message": "Too many login attempts. Please try again after 15 minutes."
        }), 429
        
    db = get_db()
    admin = db.admin_users.find_one({"email": email.strip().lower()})
    
    if not admin or not verify_password(password, admin.get("password_hash")):
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
        
    if not admin.get("is_active", True):
        return jsonify({"success": False, "message": "Account deactivated"}), 403

    access_token = generate_access_token(admin["_id"], "super_admin")
    refresh_token = generate_refresh_token(admin["_id"], "super_admin")
    
    response = jsonify({
        "success": True,
        "data": {
            "admin": AdminUser.to_public_dict(admin),
            "access_token": access_token
        }
    })
    _set_refresh_cookie(response, refresh_token)
    return response, 200

@admin_auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({
        "success": True,
        "message": "Logged out"
    })
    _clear_refresh_cookie(response)
    return response, 200

@admin_auth_bp.route('/me', methods=['GET'])
@require_admin
def me():
    # request.admin is attached by the @require_admin decorator
    admin = request.admin
    return jsonify({
        "success": True,
        "data": {
            "admin": AdminUser.to_public_dict(admin)
        }
    }), 200
