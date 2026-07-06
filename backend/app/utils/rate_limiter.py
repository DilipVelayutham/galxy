import time
from collections import defaultdict
from threading import Lock
from functools import wraps
from datetime import datetime, timezone, timedelta

from flask import request, jsonify

from backend.app import db


class RateLimiter:
    def __init__(self, limit=5, window_seconds=900):
        """
        Initialize rate limiter with attempt limit and window size.
        Default: 5 attempts per 15 minutes (900 seconds).
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.attempts = defaultdict(list)
        self.lock = Lock()

    def is_rate_limited(self, key: str) -> bool:
        """
        Checks if the key (e.g. 'ip+email') has exceeded the limit.
        Returns True if rate limited, False if allowed (and registers the attempt).
        """
        now = time.time()

        with self.lock:
            # Keep only attempts within the time window
            self.attempts[key] = [
                t for t in self.attempts[key]
                if now - t < self.window_seconds
            ]

            if len(self.attempts[key]) >= self.limit:
                return True

            self.attempts[key].append(now)
            return False


# -----------------------------------------------------------------------------
# Login Rate Limiters
# -----------------------------------------------------------------------------

login_limiter = RateLimiter(limit=5, window_seconds=900)
admin_login_limiter = RateLimiter(limit=5, window_seconds=900)


# -----------------------------------------------------------------------------
# Forgot Password Rate Limiter
# -----------------------------------------------------------------------------

def rate_limit_forgot_password(f):
    """
    Rate-limits forgot-password requests.

    Allows:
        5 requests per 15 minutes
        per IP + Email combination.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Client IP (supports reverse proxies)
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        if ip and "," in ip:
            ip = ip.split(",")[0].strip()

        # Email
        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()

        # Let route validation handle missing email
        if not email:
            return f(*args, **kwargs)

        key = f"forgot_pw:{ip}:{email}"

        now = datetime.now(timezone.utc)
        fifteen_minutes_ago = now - timedelta(minutes=15)

        try:
            # Remove expired entries
            db.rate_limits.delete_many({
                "timestamp": {
                    "$lt": fifteen_minutes_ago
                }
            })

            # Count recent attempts
            recent_requests = db.rate_limits.count_documents({
                "key": key,
                "timestamp": {
                    "$gte": fifteen_minutes_ago
                }
            })

        except Exception as e:
            # Fail-open if DB unavailable
            print(f"[Rate Limiter Warning] {e}")
            recent_requests = 0

        if recent_requests >= 5:
            return jsonify({
                "success": False,
                "message": "Too many requests. Please try again after 15 minutes.",
                "errors": {
                    "email": "Rate limit exceeded. Try again in 15 minutes."
                }
            }), 429

        try:
            db.rate_limits.insert_one({
                "key": key,
                "timestamp": now
            })
        except Exception:
            pass

        return f(*args, **kwargs)

    return decorated_function