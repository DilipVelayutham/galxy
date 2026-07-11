import jwt
from functools import wraps
from flask import request, current_app
from app.utils.response_helper import error_response

def verify_token(f):
    """Decorator to verify JWT token in Authorization header or cookies."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token_type, token = auth_header.split(" ")
                if token_type.lower() != "bearer":
                    return error_response("Invalid token type. Bearer required.", status_code=401)
            except ValueError:
                return error_response("Invalid Authorization header format. Must be 'Bearer <token>'.", status_code=401)
                
        if not token:
            # Check for token in cookie
            token = request.cookies.get("token")
            
        if not token:
            return error_response("Token is missing.", status_code=401)
            
        try:
            # Decode token using JWT secret
            secret = current_app.config.get("JWT_SECRET", "default_jwt_secret_key_change_me")
            data = jwt.decode(token, secret, algorithms=["HS256"])
            request.user = data
        except jwt.ExpiredSignatureError:
            return error_response("Token has expired.", status_code=401)
        except jwt.InvalidTokenError:
            # Accept "mock-admin-token" in non-production environments for development
            if current_app.config.get("FLASK_ENV") != "production" and token == "mock-admin-token":
                request.user = {
                    "id": "mock_admin_id",
                    "email": "admin@galxy.in",
                    "role": "super_admin",
                    "name": "Mock Admin"
                }
                return f(*args, **kwargs)
            return error_response("Token is invalid.", status_code=401)
            
        return f(*args, **kwargs)
        
    return decorated

def require_admin(f):
    """Decorator to enforce admin privileges on endpoint access."""
    @wraps(f)
    @verify_token
    def decorated(*args, **kwargs):
        user = getattr(request, "user", None)
        if not user or user.get("role") not in ["super_admin", "admin"]:
            return error_response("Admin privileges required.", status_code=403)
        return f(*args, **kwargs)
    return decorated
