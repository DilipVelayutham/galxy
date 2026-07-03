import os
import datetime
from app.database import ai_generations
from app.configs.ai_config import AI_FREE_GENERATIONS_PER_SESSION, AI_MAX_GENERATIONS_PER_USER_PER_DAY

def check_rate_limit(user_id=None, session_id=None):
    """
    Enforces the two-tier rate limiting by checking generation history in the DB.
    Cache hits (where generation_time_ms = 0) do not consume quota.
    """
    # Tier 2: Logged-in User
    if user_id:
        now = datetime.datetime.utcnow()
        today_start = datetime.datetime(now.year, now.month, now.day)
        
        try:
            count = ai_generations.count_documents({
                "user_id": user_id,
                "status": "success",
                "generation_time_ms": {"$gt": 0},
                "created_at": {"$gte": today_start}
            })
            
            if count >= AI_MAX_GENERATIONS_PER_USER_PER_DAY:
                print(f"[Rate Limit] Limit reached for User ID: {user_id} ({count}/{AI_MAX_GENERATIONS_PER_USER_PER_DAY})")
                return {
                    "allowed": False,
                    "limit_reached": True,
                    "limit_scope": "user"
                }
                
            print(f"[Rate Limit] User ID {user_id} check passed ({count}/{AI_MAX_GENERATIONS_PER_USER_PER_DAY})")
            return {
                "allowed": True,
                "limit_reached": False,
                "limit_scope": None
            }
        except Exception as e:
            print(f"[Rate Limit] Error checking user limit: {e}")
            return {
                "allowed": True,
                "limit_reached": False,
                "limit_scope": None
            }
            
    # Tier 1: Guest User (session-based)
    if session_id:
        try:
            count = ai_generations.count_documents({
                "session_id": session_id,
                "status": "success",
                "generation_time_ms": {"$gt": 0}
            })
            
            if count >= AI_FREE_GENERATIONS_PER_SESSION:
                print(f"[Rate Limit] Limit reached for Session ID: {session_id} ({count}/{AI_FREE_GENERATIONS_PER_SESSION})")
                return {
                    "allowed": False,
                    "limit_reached": True,
                    "limit_scope": "session"
                }
                
            print(f"[Rate Limit] Session ID {session_id} check passed ({count}/{AI_FREE_GENERATIONS_PER_SESSION})")
            return {
                "allowed": True,
                "limit_reached": False,
                "limit_scope": None
            }
        except Exception as e:
            print(f"[Rate Limit] Error checking session limit: {e}")
            return {
                "allowed": True,
                "limit_reached": False,
                "limit_scope": None
            }
            
    return {
        "allowed": True,
        "limit_reached": False,
        "limit_scope": None
    }
