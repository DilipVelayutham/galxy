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
from app.utils.validators import (
    validate_email,
    validate_password,
    validate_phone,
)
from app.utils.token_helper import (
    generate_access_token,
    generate_refresh_token,
    decode_token,
)


class AuthServiceError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _send_reset_email(email: str, token: str) -> bool:
    """
    Sends password reset email.
    Falls back to console logging when SMTP is not configured.
    """

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    frontend_url = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000"
    ).split(",")[0]

    reset_link = f"{frontend_url}/reset-password?token={token}"

    subject = "Reset Your Password - GALXY"

    body = f"""Hi,

You requested a password reset for your GALXY account.

Please click the link below to reset your password.

{reset_link}

This link is valid for 30 minutes.

If you didn't request this password reset, you can safely ignore this email.
"""

    # Development fallback
    if not all([smtp_host, smtp_port, smtp_email, smtp_password]):
        print("\n========== PASSWORD RESET ==========")
        print(f"To      : {email}")
        print(f"Subject : {subject}")
        print(reset_link)
        print("====================================\n")
        return True

    try:
        msg = MIMEMultipart()

        msg["From"] = smtp_email
        msg["To"] = email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.sendmail(
            smtp_email,
            email,
            msg.as_string()
        )
        server.quit()

        return True

    except Exception as e:
        print(f"[SMTP ERROR] {e}")
        return False


class AuthService:

    @staticmethod
    def signup_user(name, email, phone, password):
        """
        Customer Signup
        """

        if not name or not name.strip():
            raise AuthServiceError("Name is required", 400)

        valid_email, email_val = validate_email(email)
        if not valid_email:
            raise AuthServiceError(email_val, 400)

        valid_password, password_val = validate_password(password)
        if not valid_password:
            raise AuthServiceError(password_val, 400)

        valid_phone, phone_val = validate_phone(phone)
        if not valid_phone:
            raise AuthServiceError(phone_val, 400)

        db = get_db()

        existing_user = db.users.find_one({
            "email": email_val
        })

        if existing_user:
            raise AuthServiceError(
                "Email already registered",
                409
            )

        password_hash = hash_password(password_val)

        user_doc = User.create_document(
            name.strip(),
            email_val,
            phone_val,
            password_hash
        )

        insert_result = db.users.insert_one(user_doc)

        user_doc["_id"] = insert_result.inserted_id

        access_token = generate_access_token(
            user_doc["_id"],
            "customer"
        )

        refresh_token = generate_refresh_token(
            user_doc["_id"],
            "customer"
        )

        return (
            User.to_public_dict(user_doc),
            access_token,
            refresh_token,
        )
    @staticmethod
    def login_user(email, password):
        """
        Authenticates a customer login request.
        """

        if not email or not password:
            raise AuthServiceError(
                "Email and password are required",
                400,
            )

        valid_email, email_val = validate_email(email)

        if not valid_email:
            raise AuthServiceError(
                "Invalid email format",
                400,
            )

        db = get_db()

        user = db.users.find_one({
            "email": email_val
        })

        if not user:
            raise AuthServiceError(
                "Invalid credentials",
                401,
            )

        if not user.get("is_active", True):
            raise AuthServiceError(
                "Account deactivated",
                403,
            )

        if not verify_password(
            password,
            user.get("password_hash"),
        ):
            raise AuthServiceError(
                "Invalid credentials",
                401,
            )

        now = datetime.now(timezone.utc)

        db.users.update_one(
            {
                "_id": user["_id"]
            },
            {
                "$set": {
                    "last_login": now
                }
            }
        )

        user["last_login"] = now

        access_token = generate_access_token(
            user["_id"],
            "customer",
        )

        refresh_token = generate_refresh_token(
            user["_id"],
            "customer",
        )

        return (
            User.to_public_dict(user),
            access_token,
            refresh_token,
        )


    @staticmethod
    def refresh_tokens(refresh_token_str):
        """
        Verifies refresh token and issues
        a new access token + refresh token.
        """

        if not refresh_token_str:
            raise AuthServiceError(
                "Refresh token is missing",
                401,
            )

        try:
            payload = decode_token(refresh_token_str)

        except Exception:
            raise AuthServiceError(
                "Refresh token invalid/expired",
                401,
            )

        # Ensure correct token type
        if payload.get("type") != "refresh":
            raise AuthServiceError("Invalid token type", 401)

        # Ensure correct role
        role = payload.get("role")
        if role != "customer":
            raise AuthServiceError("Access denied", 403)

        user_id = payload.get("sub")
        db = get_db()

        user = db.users.find_one({
            "_id": ObjectId(payload["sub"])
        })

        if not user:
            raise AuthServiceError(
                "User not found",
                401,
            )

        if not user.get("is_active", True):
            raise AuthServiceError(
                "Account deactivated",
                403,
            )

        new_access = generate_access_token(
            user["_id"],
            "customer",
        )

        new_refresh = generate_refresh_token(
            user["_id"],
            "customer",
        )

        return (
            new_access,
            new_refresh,
        )


    @staticmethod
    def forgot_password(email):
        """
        Generates a secure password reset token
        and sends the recovery email.
        Always returns a generic success response
        to prevent email enumeration.
        """

        valid, email = validate_email(email)

        if not valid:
            return {
                "success": False,
                "message": email,
            }

        db = get_db()

        user = db.users.find_one({
            "email": email
        })

        if user:

            token = secrets.token_urlsafe(32)

            token_hash = hashlib.sha256(
                token.encode("utf-8")
            ).hexdigest()

            expires_at = (
                datetime.now(timezone.utc)
                + timedelta(minutes=30)
            )

            db.password_resets.insert_one({
                "email": email,
                "token_hash": token_hash,
                "expires_at": expires_at,
                "is_used": False,
                "created_at": datetime.now(timezone.utc),
            })

            _send_reset_email(
                email,
                token,
            )

        else:

            # Prevent timing attacks
            bcrypt.hashpw(
                b"dummy_password",
                bcrypt.gensalt(rounds=12),
            )

        return {
            "success": True,
            "message": "If the email is registered, a password reset link has been sent.",
        }
    @staticmethod
    def reset_password(token, new_password):
        """
        Validates a password reset token,
        updates the user's password,
        and invalidates the token.
        """

        if not token:
            return {
                "success": False,
                "message": "Token is required",
                "error_field": "token",
            }

        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        db = get_db()

        reset_record = db.password_resets.find_one({
            "token_hash": token_hash,
            "is_used": False,
        })

        if not reset_record:
            return {
                "success": False,
                "message": "Invalid or expired token",
                "error_field": "token",
            }

        expires_at = reset_record["expires_at"]

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if expires_at < datetime.now(timezone.utc):
            return {
                "success": False,
                "message": "Invalid or expired token",
                "error_field": "token",
            }

        valid, password = validate_password(
            new_password
        )

        if not valid:
            return {
                "success": False,
                "message": password,
                "error_field": "new_password",
            }

        password_hash = hash_password(password)

        update_result = db.users.update_one(
            {
                "email": reset_record["email"]
            },
            {
                "$set": {
                    "password_hash": password_hash,
                    "updated_at": datetime.now(
                        timezone.utc
                    ),
                }
            },
        )

        if update_result.matched_count == 0:
            return {
                "success": False,
                "message": "Associated user account could not be found",
                "error_field": "token",
            }

        db.password_resets.update_one(
            {
                "_id": reset_record["_id"]
            },
            {
                "$set": {
                    "is_used": True,
                    "used_at": datetime.now(
                        timezone.utc
                    ),
                }
            },
        )

        return {
            "success": True,
            "message": "Password updated successfully",
        }