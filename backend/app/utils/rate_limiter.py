from flask import request, jsonify
from functools import wraps
from datetime import datetime, timezone, timedelta
from app.configs.db import db

def rate_limit_forgot_password(f):
    """
    Custom decorator to rate-limit /forgot-password attempts.
    Allows 5 attempts per 15 minutes per IP + Email combination.
    Stores and manages state in MongoDB 'rate_limits' collection.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Determine client IP (supporting reverse proxies)
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if ip and "," in ip:
            ip = ip.split(",")[0].strip()
            
        # 2. Extract requested email
        data = request.get_json() or {}
        email = data.get('email', '').strip().lower()
        
        # If no email is provided, let standard route validation handle it
        if not email:
            return f(*args, **kwargs)
            
        key = f"forgot_pw:{ip}:{email}"
        now = datetime.now(timezone.utc)
        fifteen_minutes_ago = now - timedelta(minutes=15)
        
        try:
            # 3. Purge expired rate-limits in the DB (self-cleaning storage)
            db.rate_limits.delete_many({"timestamp": {"$lt": fifteen_minutes_ago}})
            
            # 4. Count requests made in the current window
            recent_requests = db.rate_limits.count_documents({
                "key": key,
                "timestamp": {"$gte": fifteen_minutes_ago}
            })
        except Exception as e:
            # If the database fails (e.g. timeout), fail-open to not block legitimate users
            print(f"[Rate Limiter Warning] Database check failed, skipping restriction: {str(e)}")
            recent_requests = 0
            
        if recent_requests >= 5:
            return jsonify({
                "success": False,
                "message": "Too many requests. Please try again after 15 minutes.",
                "errors": {"email": "Rate limit exceeded. Try again in 15 minutes."}
            }), 429
            
        try:
            # 5. Record the current attempt
            db.rate_limits.insert_one({
                "key": key,
                "timestamp": now
            })
        except Exception:
            pass
            
        return f(*args, **kwargs)
    return decorated_function
