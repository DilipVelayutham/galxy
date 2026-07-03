import jwt
from flask import request, jsonify
from functools import wraps
from bson import ObjectId
import os

def require_auth(f):
    """
    Decorator to protect routes requiring customer authentication.
    Decodes the JWT token from the Authorization header, verifies permissions,
    and attaches request.user.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Retrieve secret from environment variable
        jwt_secret = os.getenv("JWT_SECRET", "default_jwt_secret_for_development")
        
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"success": False, "message": "Missing Authorization header."}), 401
            
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"success": False, "message": "Invalid Authorization header format. Use: Bearer <token>."}), 401
            
        token = parts[1]
        try:
            # Decode the access token
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            user_id = payload.get("sub")
            role = payload.get("role", "customer")
            
            if role != "customer":
                return jsonify({"success": False, "message": "Access denied. Customer privileges required."}), 403
                
            from backend.app import db
            try:
                user_oid = ObjectId(user_id)
            except Exception:
                return jsonify({"success": False, "message": "Invalid user ID format in token."}), 401
                
            user = db.users.find_one({"_id": user_oid})
            if not user:
                return jsonify({"success": False, "message": "User not found."}), 401
                
            if not user.get("is_active", True):
                return jsonify({"success": False, "message": "Account has been deactivated."}), 403
                
            # Attach user to Flask request context
            request.user = user
            
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Access token has expired."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token."}), 401
        except Exception as e:
            return jsonify({"success": False, "message": f"Authentication failed: {str(e)}"}), 401
            
        return f(*args, **kwargs)
    return decorated
