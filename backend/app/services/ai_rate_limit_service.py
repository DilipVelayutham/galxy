import os
import datetime
from app.database import ai_generations
from app.configs.ai_config import AI_FREE_GENERATIONS_PER_SESSION, AI_MAX_GENERATIONS_PER_USER_PER_DAY

def check_rate_limit(user_id=None, session_id=None, ip_address=None):
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
                "status": {"$in": ["success", "failed"]},
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
            
    # Tier 1: Guest User (session-based & IP-based fallback to prevent bypass)
    if session_id or ip_address:
        try:
            # 1. Check Session ID limit
            if session_id:
                count = ai_generations.count_documents({
                    "session_id": session_id,
                    "status": {"$in": ["success", "failed"]},
                    "generation_time_ms": {"$gt": 0}
                })
                
                if count >= AI_FREE_GENERATIONS_PER_SESSION:
                    print(f"[Rate Limit] Limit reached for Session ID: {session_id} ({count}/{AI_FREE_GENERATIONS_PER_SESSION})")
                    return {
                        "allowed": False,
                        "limit_reached": True,
                        "limit_scope": "session"
                    }
            
            # 2. Check IP Address limit within rolling 24h (only count guest requests)
            if ip_address:
                twenty_four_hours_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
                ip_count = ai_generations.count_documents({
                    "ip_address": ip_address,
                    "status": {"$in": ["success", "failed"]},
                    "generation_time_ms": {"$gt": 0},
                    "user_id": None,
                    "created_at": {"$gte": twenty_four_hours_ago}
                })
                
                if ip_count >= AI_FREE_GENERATIONS_PER_SESSION:
                    print(f"[Rate Limit] Limit reached for IP Address: {ip_address} ({ip_count}/{AI_FREE_GENERATIONS_PER_SESSION} in 24h)")
                    return {
                        "allowed": False,
                        "limit_reached": True,
                        # Fold IP-based block into session scope to adhere to frontend two-valued contract
                        "limit_scope": "session"
                    }
                    
            print(f"[Rate Limit] Guest check passed for Session ID: {session_id}, IP: {ip_address}")
            return {
                "allowed": True,
                "limit_reached": False,
                "limit_scope": None
            }
        except Exception as e:
            print(f"[Rate Limit] Error checking guest limits: {e}")
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
