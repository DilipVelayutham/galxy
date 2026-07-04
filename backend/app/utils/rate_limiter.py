import time
from collections import defaultdict
from threading import Lock

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
            self.attempts[key] = [t for t in self.attempts[key] if now - t < self.window_seconds]
            
            if len(self.attempts[key]) >= self.limit:
                return True
            
            self.attempts[key].append(now)
            return False

# Central rate limiters for customer login and admin login
login_limiter = RateLimiter(limit=5, window_seconds=900)
admin_login_limiter = RateLimiter(limit=5, window_seconds=900)
