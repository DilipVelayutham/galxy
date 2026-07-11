from flask import Blueprint, request, jsonify, make_response, g
import jwt
from app.services.auth_service import AuthService
from app.middleware.auth import require_auth
from app.config import Config
from app.utils.rate_limiter import rate_limit_forgot_password

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
    if status == 201:
        tokens = res["data"]
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        user = tokens["user"]
        
        resp = make_response(jsonify({
            "success": True,
            "data": {
                "user": user,
                "access_token": access_token
            }
        }), 201)
        
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
        if payload.get("type") != "refresh":
            return jsonify({
                "success": False,
                "message": "Invalid token type",
                "errors": {"refresh_token": "Invalid token type"}
            }), 401
            
        user_id = payload.get("sub") or payload.get("user_id")
        
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
        return jsonify({"success": False, "message": "Refresh token is invalid/expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "message": "Invalid refresh token"}), 401

@auth_bp.route("/forgot-password", methods=["POST"])
@rate_limit_forgot_password
def forgot_password():
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required",
            "errors": {"email": "Email is required"}
        }), 400
        
    res = AuthService.forgot_password(email)
    return jsonify(res), 200

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    token = data.get("token")
    new_password = data.get("new_password")
    
    if not token or not new_password:
        errors = {}
        if not token:
            errors["token"] = "Token is required"
        if not new_password:
            errors["new_password"] = "New password is required"
        return jsonify({
            "success": False,
            "message": "Missing required fields",
            "errors": errors
        }), 400
        
    res = AuthService.reset_password(token, new_password)
    if not res.get("success"):
        error_field = res.get("error_field") or "token"
        return jsonify({
            "success": False,
            "message": res.get("message", "Password reset failed"),
            "errors": {error_field: res.get("message")}
        }), 400
        
    return jsonify(res), 200

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
