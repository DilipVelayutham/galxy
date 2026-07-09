from flask import Blueprint, request, jsonify, make_response, g
import jwt
from app.services.auth_service import AuthService
from app.middleware.auth import require_auth
from app.config import Config

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    
    if not name or not email or not phone or not password:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
        
    res, status = AuthService.signup(name, email, phone, password)
    return jsonify(res), status

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400
        
    res, status = AuthService.login(email, password)
    if status == 200:
        # Extract refresh token
        tokens = res["data"]
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        user = tokens["user"]
        
        # Prepare response
        resp = make_response(jsonify({
            "success": True,
            "data": {
                "user": user,
                "access_token": access_token
            }
        }), 200)
        
        # Set refresh token in HttpOnly cookie
        resp.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=True,
            samesite="Strict",
            path="/api/auth",
            max_age=7 * 24 * 60 * 60 # 7 days
        )
        return resp
        
    return jsonify(res), status

@auth_bp.route("/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"success": True, "message": "Logged out successfully"}), 200)
    resp.set_cookie(
        "refresh_token",
        "",
        httponly=True,
        secure=True,
        samesite="Strict",
        path="/api/auth",
        expires=0
    )
    return resp

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    # Attempt to read refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return jsonify({"success": False, "message": "Refresh token is missing"}), 401
        
    try:
        payload = jwt.decode(refresh_token, Config.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        
        # Look up user to check role
        from app.db import db
        from bson import ObjectId
        
        # Check admin first
        admin = db.admin_users.find_one({"_id": ObjectId(user_id)})
        if admin:
            role = admin.get("role", "super_admin")
            email = admin["email"]
            name = admin["name"]
        else:
            user = db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return jsonify({"success": False, "message": "User not found"}), 401
            role = "customer"
            email = user["email"]
            name = user["name"]
            
        # Issue new access token
        new_access = AuthService.generate_access_token(user_id, email, role)
        
        return jsonify({
            "success": True,
            "data": {
                "user": {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "role": role
                },
                "access_token": new_access
            }
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"success": False, "message": "Refresh token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "message": "Invalid refresh token"}), 401

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    # Anti-enumeration response
    return jsonify({
        "success": True,
        "message": "If that email exists in our system, a reset link has been sent."
    }), 200

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    # Stub reset-password endpoint
    return jsonify({
        "success": True,
        "message": "Password reset successful."
    }), 200

@auth_bp.route("/profile", methods=["GET"])
@require_auth
def profile_get():
    res, status = AuthService.get_profile(g.user["id"], g.user["role"])
    return jsonify(res), status

@auth_bp.route("/profile", methods=["PUT"])
@require_auth
def profile_put():
    data = request.get_json() or {}
    name = data.get("name")
    phone = data.get("phone")
    
    if not name:
        return jsonify({"success": False, "message": "Name is required"}), 400
        
    res, status = AuthService.update_profile(g.user["id"], g.user["role"], name, phone)
    return jsonify(res), status

@auth_bp.route("/addresses", methods=["POST"])
@require_auth
def addresses_post():
    data = request.get_json() or {}
    required = ["line1", "city", "state", "pincode"]
    if not all(k in data for k in required):
        return jsonify({"success": False, "message": "Missing address details"}), 400
        
    res, status = AuthService.add_address(g.user["id"], data)
    return jsonify(res), status

@auth_bp.route("/addresses/<id>", methods=["PUT"])
@require_auth
def addresses_put(id):
    data = request.get_json() or {}
    res, status = AuthService.update_address(g.user["id"], id, data)
    return jsonify(res), status

@auth_bp.route("/addresses/<id>", methods=["DELETE"])
@require_auth
def addresses_delete(id):
    res, status = AuthService.delete_address(g.user["id"], id)
    return jsonify(res), status
