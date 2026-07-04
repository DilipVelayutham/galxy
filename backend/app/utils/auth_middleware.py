import functools
from flask import request, jsonify
from app.utils.token_helper import decode_token, ExpiredTokenError, InvalidTokenError
from app.db import get_db
from bson import ObjectId

def require_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Missing or invalid authorization header", "errors": {}}), 401
        
        token = auth_header.split(" ")[1]
        try:
            payload = decode_token(token)
            role = payload.get("role")
            if role != "customer":
                return jsonify({"success": False, "message": "Access denied. Customers only.", "errors": {}}), 403
            
            user_id = payload.get("sub")
            db = get_db()
            user = db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return jsonify({"success": False, "message": "User not found", "errors": {}}), 401
            if not user.get("is_active", True):
                return jsonify({"success": False, "message": "Account deactivated", "errors": {}}), 403
            
            # Attach to request context
            request.user = user
            return f(*args, **kwargs)
        except ExpiredTokenError:
            return jsonify({"success": False, "message": "Token has expired", "errors": {}}), 401
        except InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token", "errors": {}}), 401
        except Exception as e:
            return jsonify({"success": False, "message": f"Authentication failed: {str(e)}", "errors": {}}), 401
    return decorated

def require_admin(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Missing or invalid authorization header", "errors": {}}), 401
        
        token = auth_header.split(" ")[1]
        try:
            payload = decode_token(token)
            role = payload.get("role")
            if role != "super_admin":
                return jsonify({"success": False, "message": "Access denied. Admins only.", "errors": {}}), 403
            
            admin_id = payload.get("sub")
            db = get_db()
            admin = db.admin_users.find_one({"_id": ObjectId(admin_id)})
            if not admin:
                return jsonify({"success": False, "message": "Admin not found", "errors": {}}), 401
            if not admin.get("is_active", True):
                return jsonify({"success": False, "message": "Account deactivated", "errors": {}}), 403
            
            # Attach to request context
            request.admin = admin
            return f(*args, **kwargs)
        except ExpiredTokenError:
            return jsonify({"success": False, "message": "Token has expired", "errors": {}}), 401
        except InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token", "errors": {}}), 401
        except Exception as e:
            return jsonify({"success": False, "message": f"Authentication failed: {str(e)}", "errors": {}}), 401
    return decorated

def optional_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        request.user = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = decode_token(token)
                role = payload.get("role")
                if role == "customer":
                    user_id = payload.get("sub")
                    db = get_db()
                    user = db.users.find_one({"_id": ObjectId(user_id)})
                    if user and user.get("is_active", True):
                        request.user = user
            except Exception:
                pass
        return f(*args, **kwargs)
    return decorated
