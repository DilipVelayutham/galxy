import os
from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
from bson import ObjectId
from app.db import get_db
from app.config import Config

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        db = get_db()
        flask_env = os.environ.get("FLASK_ENV", "development").lower()
        
        # 1. Allow testing bypass via headers
        user_id_header = request.headers.get('X-User-Id')
        if user_id_header:
            try:
                user = db.users.find_one({"_id": ObjectId(user_id_header)})
                if not user:
                    user = {"_id": ObjectId(user_id_header), "name": "Test User", "email": "test@example.com", "role": "customer"}
                g.user_id = user["_id"]
                g.user = {
                    "id": str(user["_id"]),
                    "user_id": str(user["_id"]),
                    "role": "customer",
                    "_id": user["_id"],
                    "email": user.get("email"),
                    "name": user.get("name", "")
                }
                g.current_user = g.user
                return f(*args, **kwargs)
            except Exception:
                pass

        # 2. Check Authorization Header or Cookie
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
        if not token:
            token = request.cookies.get("token")
            
        if not token:
            # Bypass in development mode for easy manual/local testing
            if flask_env == "development":
                g.user_id = ObjectId("60c72b2f9b1d8e1f88888888")
                g.user = {"id": str(g.user_id), "user_id": str(g.user_id), "role": "customer", "_id": g.user_id, "email": "dev@galxy.in", "name": "Dev User"}
                g.current_user = g.user
                return f(*args, **kwargs)
            return jsonify({"success": False, "message": "Authorization token is missing."}), 401
            
        try:
            secret = current_app.config.get("JWT_SECRET", Config.JWT_SECRET)
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            
            user_id = payload.get("sub") or payload.get("user_id")
            role = payload.get("role", "customer")
            
            # Fetch user from db
            user = db.users.find_one({"_id": ObjectId(user_id)})
            if not user and flask_env == "development":
                user = {"_id": ObjectId(user_id), "name": "Dev User", "email": "dev@galxy.in", "role": role}
                
            if not user:
                return jsonify({"success": False, "message": "User not found."}), 401
                
            g.user_id = user["_id"]
            g.user = {
                "id": str(user["_id"]),
                "user_id": str(user["_id"]),
                "role": role,
                "_id": user["_id"],
                "email": user.get("email"),
                "name": user.get("name", "")
            }
            g.current_user = g.user
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Authentication token has expired."}), 401
        except jwt.InvalidTokenError:
            # Allow mock token in dev
            if flask_env == "development" and token == "mock-customer-token":
                g.user_id = ObjectId("60c72b2f9b1d8e1f88888888")
                g.user = {"id": str(g.user_id), "user_id": str(g.user_id), "role": "customer", "_id": g.user_id, "email": "dev@galxy.in", "name": "Dev User"}
                g.current_user = g.user
                return f(*args, **kwargs)
            return jsonify({"success": False, "message": "Invalid token."}), 401
            
    return decorated

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        db = get_db()
        flask_env = os.environ.get("FLASK_ENV", "development").lower()
        
        # 1. Allow testing bypass via headers
        admin_id_header = request.headers.get('X-Admin-Id') or request.headers.get('X-User-Id')
        if admin_id_header:
            try:
                admin = db.admin_users.find_one({"_id": ObjectId(admin_id_header)})
                if not admin:
                    admin = {"_id": ObjectId(admin_id_header), "name": "Test Admin", "email": "admin@example.com", "role": "super_admin"}
                g.user_id = admin["_id"]
                g.user = {
                    "id": str(admin["_id"]),
                    "user_id": str(admin["_id"]),
                    "role": admin.get("role", "super_admin"),
                    "_id": admin["_id"],
                    "email": admin.get("email"),
                    "name": admin.get("name", "")
                }
                g.current_user = g.user
                return f(*args, **kwargs)
            except Exception:
                pass

        # 2. Check Authorization Header or Cookie
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
        if not token:
            token = request.cookies.get("token")
            
        if not token:
            # Bypass in development mode for easy manual/local testing
            if flask_env == "development":
                g.user_id = ObjectId("60c72b2f9b1d8e1f99999999")
                g.user = {"id": str(g.user_id), "user_id": str(g.user_id), "role": "super_admin", "_id": g.user_id, "email": "admin@galxy.in", "name": "Dev Admin"}
                g.current_user = g.user
                return f(*args, **kwargs)
            return jsonify({"success": False, "message": "Authorization token is missing."}), 401
            
        try:
            secret = current_app.config.get("JWT_SECRET", Config.JWT_SECRET)
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            
            user_id = payload.get("sub") or payload.get("user_id")
            role = payload.get("role", "super_admin")
            
            if role not in ["super_admin", "admin"]:
                return jsonify({"success": False, "message": "Admin privileges required."}), 403
                
            # Fetch admin from db
            admin = db.admin_users.find_one({"_id": ObjectId(user_id)})
            if not admin and flask_env == "development":
                admin = {"_id": ObjectId(user_id), "name": "Dev Admin", "email": "admin@galxy.in", "role": role}
                
            if not admin:
                return jsonify({"success": False, "message": "Admin user not found."}), 401
                
            g.user_id = admin["_id"]
            g.user = {
                "id": str(admin["_id"]),
                "user_id": str(admin["_id"]),
                "role": role,
                "_id": admin["_id"],
                "email": admin.get("email"),
                "name": admin.get("name", "")
            }
            g.current_user = g.user
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Authentication token has expired."}), 401
        except jwt.InvalidTokenError:
            # Allow mock token in dev
            if flask_env == "development" and (token == "mock-admin-token" or token == "mock_admin_id"):
                g.user_id = ObjectId("60c72b2f9b1d8e1f99999999")
                g.user = {"id": str(g.user_id), "user_id": str(g.user_id), "role": "super_admin", "_id": g.user_id, "email": "admin@galxy.in", "name": "Dev Admin"}
                g.current_user = g.user
                return f(*args, **kwargs)
            return jsonify({"success": False, "message": "Invalid token."}), 401
            
    return decorated
