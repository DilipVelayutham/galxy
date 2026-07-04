from datetime import datetime, timezone, timedelta
import os
import secrets
import hashlib
import smtplib
import bcrypt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

def _send_reset_email(email: str, token: str) -> bool:
    """
    Sends a password reset email using SMTP.
    If SMTP configuration is missing, it falls back to a development console logger (mock).
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    # Construct reset link pointing to the Next.js frontend
    frontend_url = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")[0]
    reset_link = f"{frontend_url}/reset-password?token={token}"
    
    subject = "Reset Your Password - GALXY"
    body = f"""Hi,

You requested a password reset for your GALXY account.
Please click the link below to reset your password. This link is valid for 30 minutes.

{reset_link}

If you did not request this, please ignore this email.
"""
    
    # Fallback to local console log if SMTP credentials are not configured
    if not all([smtp_host, smtp_port, smtp_email, smtp_password]):
        print(f"\n--- [SMTP MOCK EMAIL] ---")
        print(f"To: {email}")
        print(f"Subject: {subject}")
        print(f"Reset Link: {reset_link}")
        print(f"-------------------------\n")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[SMTP ERROR] Failed to send recovery email: {str(e)}")
        return False

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

    @staticmethod
    def forgot_password(email):
        """
        Generates a secure password reset token and emails it.
        Prevents email enumeration attacks.
        """
        # 1. Validate email format
        is_valid, email_normalized = validate_email(email)
        if not is_valid:
            return {
                "success": False,
                "message": email_normalized
            }

        db = get_db()
        # 2. Check if user exists in the database
        user = db.users.find_one({"email": email_normalized})

        if user:
            # A. User exists: generate and save token
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
            
            # 30-minute expiration
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
            
            # Insert into password_resets collection
            db.password_resets.insert_one({
                "email": email_normalized,
                "token_hash": token_hash,
                "expires_at": expires_at,
                "is_used": False,
                "created_at": datetime.now(timezone.utc)
            })
            
            # B. Send recovery email
            _send_reset_email(email_normalized, token)
        else:
            # B. User does not exist: simulate bcrypt time delay to prevent timing analysis
            dummy_pw = "dummy_password_for_timing_mitigation"
            bcrypt.hashpw(dummy_pw.encode('utf-8'), bcrypt.gensalt(rounds=12))

        # Always return a generic success message
        return {
            "success": True,
            "message": "If the email is registered, a password reset link has been sent."
        }

    @staticmethod
    def reset_password(token, new_password):
        """
        Validates the token, validates the new password, hashes it,
        updates user record, and invalidates the token.
        """
        if not token:
            return {
                "success": False,
                "message": "Token is required"
            }

        # 1. Hash the incoming token to match database storage
        token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
        
        db = get_db()
        # 2. Look up the reset record
        reset_record = db.password_resets.find_one({
            "token_hash": token_hash,
            "is_used": False
        })
        
        if not reset_record:
            return {
                "success": False,
                "message": "Invalid or expired token"
            }

        # 3. Check expiration
        now = datetime.now(timezone.utc)
        expires_at = reset_record["expires_at"]
        
        # Ensure timezone-aware datetime comparison
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            
        if expires_at < now:
            return {
                "success": False,
                "message": "Invalid or expired token"
            }

        # 4. Validate new password strength
        is_valid, err_msg = validate_password(new_password)
        if not is_valid:
            return {
                "success": False,
                "message": err_msg
            }

        # 5. Hash the password and update the user record
        hashed_pw = hash_password(new_password)
        update_result = db.users.update_one(
            {"email": reset_record["email"]},
            {"$set": {
                "password_hash": hashed_pw,
                "updated_at": datetime.now(timezone.utc)
            }}
        )

        if update_result.matched_count == 0:
            return {
                "success": False,
                "message": "Associated user account could not be found"
            }

        # 6. Invalidate the token (single-use constraint)
        db.password_resets.update_one(
            {"_id": reset_record["_id"]},
            {"$set": {
                "is_used": True,
                "used_at": datetime.now(timezone.utc)
            }}
        )

        return {
            "success": True,
            "message": "Password updated successfully"
        }
