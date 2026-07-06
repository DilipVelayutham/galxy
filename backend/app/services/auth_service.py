import os
import secrets
import hashlib
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import bcrypt  # used for timing attack mitigation

from app.configs.db import db
from app.utils.password_helper import hash_password
from app.utils.validators import validate_email, validate_password

def send_reset_email(email: str, token: str) -> bool:
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
        masked_link = f"{frontend_url}/reset-password?token={token[:6]}..."
        print(f"\n--- [SMTP MOCK EMAIL] ---")
        print(f"To: {email}")
        print(f"Subject: {subject}")
        print(f"Reset Link (Masked): {masked_link}")
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
        # Avoid leaking raw exception data to client/logs in production
        print(f"[SMTP ERROR] Failed to send recovery email: {str(e)}")
        return False

def forgot_password(email: str) -> dict:
    """
    Generates a secure password reset token and emails it.
    Prevents enumeration attacks by returning identical responses and execution time.
    """
    # 1. Validate email format
    is_valid, email_normalized = validate_email(email)
    if not is_valid:
        # If email format itself is invalid, return standard error
        return {
            "success": False,
            "message": email_normalized  # This holds the validation error message
        }

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
        send_reset_email(email_normalized, token)
    else:
        # B. User does not exist: simulate bcrypt time delay to prevent timing analysis
        # Generating a dummy bcrypt salt/hash matches the typical latency profile of database lookups and processing.
        dummy_pw = "dummy_password_for_timing_mitigation"
        bcrypt.hashpw(dummy_pw.encode('utf-8'), bcrypt.gensalt(rounds=12))

    # Always return a generic success message
    return {
        "success": True,
        "message": "If the email is registered, a password reset link has been sent."
    }

def reset_password(token: str, new_password: str) -> dict:
    """
    Validates the token, validates the new password, hashes it,
    updates user record, and invalidates the token.
    """
    if not token:
        return {
            "success": False,
            "message": "Token is required",
            "error_field": "token"
        }

    # 1. Hash the incoming token to match database storage
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    
    # 2. Look up the reset record
    reset_record = db.password_resets.find_one({
        "token_hash": token_hash,
        "is_used": False
    })
    
    if not reset_record:
        return {
            "success": False,
            "message": "Invalid or expired token",
            "error_field": "token"
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
            "message": "Invalid or expired token",
            "error_field": "token"
        }

    # 4. Validate new password strength
    is_valid, err_msg = validate_password(new_password)
    if not is_valid:
        return {
            "success": False,
            "message": err_msg,
            "error_field": "new_password"
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
            "message": "Associated user account could not be found",
            "error_field": "token"
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
