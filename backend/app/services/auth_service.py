from datetime import datetime, timezone
from bson import ObjectId
from app.db import get_db
from app.models.user import User
from app.utils.password_helper import hash_password, verify_password
from app.utils.validators import validate_email, validate_password, validate_phone
from app.utils.token_helper import generate_access_token, generate_refresh_token, decode_token

class AuthServiceError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class AuthService:
    @staticmethod
    def signup_user(name, email, phone, password):
        """
        Signs up a new customer user.
        """
        # Validate inputs
        if not name or not name.strip():
            raise AuthServiceError("Name is required", 400)
        
        valid_email, email_val = validate_email(email)
        if not valid_email:
            raise AuthServiceError(email_val, 400)
            
        valid_pass, pass_val = validate_password(password)
        if not valid_pass:
            raise AuthServiceError(pass_val, 400)
            
        valid_phone, phone_val = validate_phone(phone)
        if not valid_phone:
            raise AuthServiceError(phone_val, 400)

        db = get_db()
        # Enforce unique email index (case-insensitive checks)
        existing_user = db.users.find_one({"email": email_val})
        if existing_user:
            raise AuthServiceError("Email already registered", 409)

        # Hash password and insert
        pw_hash = hash_password(pass_val)
        user_doc = User.create_document(name.strip(), email_val, phone_val, pw_hash)
        
        insert_result = db.users.insert_one(user_doc)
        user_doc["_id"] = insert_result.inserted_id

        # Generate tokens
        access_token = generate_access_token(user_doc["_id"], "customer")
        refresh_token = generate_refresh_token(user_doc["_id"], "customer")

        return User.to_public_dict(user_doc), access_token, refresh_token

    @staticmethod
    def login_user(email, password):
        """
        Authenticates a customer login request.
        """
        if not email or not password:
            raise AuthServiceError("Email and password are required", 400)

        valid_email, email_val = validate_email(email)
        if not valid_email:
            raise AuthServiceError("Invalid email format", 400)

        db = get_db()
        user = db.users.find_one({"email": email_val})
        if not user:
            raise AuthServiceError("Invalid credentials", 401)

        if not user.get("is_active", True):
            raise AuthServiceError("Account deactivated", 403)

        if not verify_password(password, user.get("password_hash")):
            raise AuthServiceError("Invalid credentials", 401)

        # Update last login
        now = datetime.now(timezone.utc)
        db.users.update_one({"_id": user["_id"]}, {"$set": {"last_login": now}})
        user["last_login"] = now

        # Generate tokens
        access_token = generate_access_token(user["_id"], "customer")
        refresh_token = generate_refresh_token(user["_id"], "customer")

        return User.to_public_dict(user), access_token, refresh_token

    @staticmethod
    def refresh_tokens(refresh_token_str):
        """
        Verifies refresh token and issues a new access token and rotated refresh token.
        """
        if not refresh_token_str:
            raise AuthServiceError("Refresh token is missing", 401)

        try:
            payload = decode_token(refresh_token_str)
        except Exception:
            raise AuthServiceError("Refresh token invalid/expired", 401)

        # Ensure correct token type
        if payload.get("type") != "refresh":
            raise AuthServiceError("Invalid token type", 401)

        # Ensure correct role
        role = payload.get("role")
        if role != "customer":
            raise AuthServiceError("Access denied", 403)

        user_id = payload.get("sub")
        db = get_db()
        user = db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise AuthServiceError("User not found", 401)
            
        if not user.get("is_active", True):
            raise AuthServiceError("Account deactivated", 403)

        # Issue new tokens (rotation)
        new_access = generate_access_token(user["_id"], "customer")
        new_refresh = generate_refresh_token(user["_id"], "customer")

        return new_access, new_refresh

    # =========================================================================
    # Stubs for In3 (Tharani) Password Recovery Flow
    # =========================================================================
    @staticmethod
    def forgot_password(email):
        """
        Placeholder service for forgot password flow.
        """
        # Tharani will implement email verification, token generation & SMTP send.
        pass

    @staticmethod
    def reset_password(token, new_password):
        """
        Placeholder service for reset password flow.
        """
        # Tharani will implement token verification, password hashing & update.
        pass
