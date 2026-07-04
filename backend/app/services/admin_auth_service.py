from datetime import datetime, timezone
from bson import ObjectId
from app.db import get_db
from app.models.admin_user import AdminUser
from app.utils.password_helper import verify_password
from app.utils.token_helper import generate_access_token, generate_refresh_token, decode_token

class AdminAuthServiceError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class AdminAuthService:
    @staticmethod
    def login_admin(email, password):
        """
        Authenticates an admin user login request.
        """
        if not email or not password:
            raise AdminAuthServiceError("Email and password are required", 400)

        db = get_db()
        admin = db.admin_users.find_one({"email": email.strip().lower()})
        
        if not admin or not verify_password(password, admin.get("password_hash")):
            raise AdminAuthServiceError("Invalid credentials", 401)

        if not admin.get("is_active", True):
            raise AdminAuthServiceError("Account deactivated", 403)

        # Update last login
        now = datetime.now(timezone.utc)
        db.admin_users.update_one({"_id": admin["_id"]}, {"$set": {"last_login": now}})
        admin["last_login"] = now

        # Generate tokens
        access_token = generate_access_token(admin["_id"], "super_admin")
        refresh_token = generate_refresh_token(admin["_id"], "super_admin")

        return AdminUser.to_public_dict(admin), access_token, refresh_token

    @staticmethod
    def get_admin_profile(admin_id):
        """
        Retrieves the profile of an admin user.
        """
        db = get_db()
        admin = db.admin_users.find_one({"_id": ObjectId(admin_id)})
        if not admin:
            raise AdminAuthServiceError("Admin not found", 404)
        return AdminUser.to_public_dict(admin)

    @staticmethod
    def refresh_admin_tokens(refresh_token_str):
        """
        Verifies refresh token and issues a new access token and rotated refresh token for admin.
        """
        if not refresh_token_str:
            raise AdminAuthServiceError("Refresh token is missing", 401)

        try:
            payload = decode_token(refresh_token_str)
        except Exception:
            raise AdminAuthServiceError("Refresh token invalid/expired", 401)

        # Ensure correct token type and role
        if payload.get("type") != "refresh":
            raise AdminAuthServiceError("Invalid token type", 401)

        role = payload.get("role")
        if role != "super_admin":
            raise AdminAuthServiceError("Access denied. Admins only.", 403)

        admin_id = payload.get("sub")
        db = get_db()
        admin = db.admin_users.find_one({"_id": ObjectId(admin_id)})
        
        if not admin:
            raise AdminAuthServiceError("Admin not found", 401)
            
        if not admin.get("is_active", True):
            raise AdminAuthServiceError("Account deactivated", 403)

        # Issue new tokens (rotation)
        new_access = generate_access_token(admin["_id"], "super_admin")
        new_refresh = generate_refresh_token(admin["_id"], "super_admin")

        return new_access, new_refresh
