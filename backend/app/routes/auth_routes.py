import os
from flask import Blueprint, request, jsonify, make_response
from app.services.auth_service import AuthService, AuthServiceError

auth_bp = Blueprint('auth', __name__)

COOKIE_NAME = 'refresh_token'

def _set_refresh_cookie(response, refresh_token):
    is_prod = os.getenv("FLASK_ENV", "development") == "production"
    response.set_cookie(
        key=COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=is_prod,
        samesite='Lax',  # Lax is necessary for local cross-port dev (localhost:3000 -> localhost:5000)
        max_age=30 * 24 * 60 * 60,  # 30 days
        path='/api/auth'  # Keep cookie scoped to the auth endpoints for security
    )

def _clear_refresh_cookie(response):
    is_prod = os.getenv("FLASK_ENV", "development") == "production"
    response.delete_cookie(
        key=COOKIE_NAME,
        path='/api/auth',
        secure=is_prod,
        samesite='Lax'
    )

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    try:
        user, access_token, refresh_token = AuthService.signup_user(
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            password=data.get("password")
        )
        
        response = jsonify({
            "success": True,
            "message": "Account created",
            "data": {
                "user": user,
                "access_token": access_token
            }
        })
        _set_refresh_cookie(response, refresh_token)
        return response, 201
    except AuthServiceError as e:
        return jsonify({
            "success": False,
            "message": e.message,
            "errors": { "auth": e.message }
        }), e.status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Signup failed: {str(e)}",
            "errors": {}
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400
        
    # Rate limiting on IP + Email combo
    ip_addr = request.remote_addr or "unknown_ip"
    rate_key = f"{ip_addr}+{email.strip().lower()}"
    from app.utils.rate_limiter import login_limiter
    if login_limiter.is_rate_limited(rate_key):
        return jsonify({
            "success": False,
            "message": "Too many login attempts. Please try again after 15 minutes."
        }), 429

    try:
        user, access_token, refresh_token = AuthService.login_user(
            email=email,
            password=data.get("password")
        )
        
        response = jsonify({
            "success": True,
            "data": {
                "user": user,
                "access_token": access_token
            }
        })
        _set_refresh_cookie(response, refresh_token)
        return response, 200
    except AuthServiceError as e:
        return jsonify({
            "success": False,
            "message": e.message,
            "errors": { "auth": e.message }
        }), e.status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Login failed: {str(e)}",
            "errors": {}
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({
        "success": True,
        "message": "Logged out"
    })
    _clear_refresh_cookie(response)
    return response, 200

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.cookies.get(COOKIE_NAME)
    try:
        new_access, new_refresh = AuthService.refresh_tokens(refresh_token)
        response = jsonify({
            "success": True,
            "data": {
                "access_token": new_access
            }
        })
        _set_refresh_cookie(response, new_refresh)
        return response, 200
    except AuthServiceError as e:
        # If refresh token fails, clear cookie and force re-login
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

# =========================================================================
# Stubs for In3 (Tharani) Password Recovery Endpoints
# =========================================================================
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Placeholder endpoint for forgot password.
    Should always return 200 to prevent email enumeration attacks.
    """
    # Tharani will parse request body: { "email" } and call AuthService.forgot_password
    # Returning a generic message:
    return jsonify({
        "success": True,
        "message": "If this email is registered, a password reset link has been sent."
    }), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Placeholder endpoint for reset password.
    """
    # Tharani will parse request body: { "token", "new_password" }
    return jsonify({
        "success": True,
        "message": "Password updated"
    }), 200
