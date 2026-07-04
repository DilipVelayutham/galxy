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

from app.services.admin_auth_service import AdminAuthService, AdminAuthServiceError

@admin_auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required", "errors": {}}), 400
        
    # Rate limiting on IP + Email combo
    ip_addr = request.remote_addr or "unknown_ip"
    rate_key = f"{ip_addr}+{email.strip().lower()}"
    from app.utils.rate_limiter import admin_login_limiter
    if admin_login_limiter.is_rate_limited(rate_key):
        return jsonify({
            "success": False,
            "message": "Too many login attempts. Please try again after 15 minutes.",
            "errors": {}
        }), 429
        
    try:
        admin_dict, access_token, refresh_token = AdminAuthService.login_admin(email, password)
        response = jsonify({
            "success": True,
            "data": {
                "admin": admin_dict,
                "access_token": access_token
            }
        })
        _set_refresh_cookie(response, refresh_token)
        return response, 200
    except AdminAuthServiceError as e:
        return jsonify({
            "success": False,
            "message": e.message,
            "errors": {}
        }), e.status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Admin login failed: {str(e)}",
            "errors": {}
        }), 500

@admin_auth_bp.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.cookies.get(COOKIE_NAME)
    try:
        new_access, new_refresh = AdminAuthService.refresh_admin_tokens(refresh_token)
        response = jsonify({
            "success": True,
            "data": {
                "access_token": new_access
            }
        })
        _set_refresh_cookie(response, new_refresh)
        return response, 200
    except AdminAuthServiceError as e:
        response = jsonify({
            "success": False,
            "message": e.message,
            "errors": {}
        })
        _clear_refresh_cookie(response)
        return response, e.status_code
    except Exception as e:
        response = jsonify({
            "success": False,
            "message": f"Token refresh failed: {str(e)}",
            "errors": {}
        })
        _clear_refresh_cookie(response)
        return response, 500

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
