<<<<<<< HEAD
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
=======
"""
ai_rate_limit_service.py — Module 5 AI Preview Generation
Two-tier rate limiting: guest (session_id) + logged-in user (daily cap).

Counts successful, genuine (non-cached) provider generations directly from
the MongoDB 'ai_generations' collection to verify usage quotas.
"""
import logging
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from bson import ObjectId
from app.db import get_db
from app.configs.ai_config import (
    AI_FREE_GENERATIONS_PER_SESSION,
    AI_MAX_GENERATIONS_PER_USER_PER_DAY,
)

logger = logging.getLogger(__name__)


@dataclass
class RateLimitResult:
    """
    Result of a rate-limit check.
    Fields match the 429 response shape required by the frontend (spec §9, §12).
    """
    allowed: bool
    limit_reached: bool
    limit_scope: str   # "guest" | "user" | ""
    message: str       # human-readable message for the frontend upsell UI


def _get_generations_collection():
    """Return the ai_generations collection from MongoDB."""
    return get_db()["ai_generations"]


def check_rate_limit(session_id: str, user_id: str | None) -> RateLimitResult:
    """
    Check whether this session/user may trigger a new AI generation.

    Per spec §8: cached hits should NOT call this function — only new
    provider calls consume quota.

    Quotas:
      - Guest (session_id): AI_FREE_GENERATIONS_PER_SESSION total across all time.
      - Logged-in (user_id): AI_MAX_GENERATIONS_PER_USER_PER_DAY per UTC calendar day.
    """
    col = _get_generations_collection()

    # 1. Logged-in user limit check (Daily)
    if user_id:
        try:
            user_oid = ObjectId(user_id)
        except Exception:
            logger.warning("[rate_limit] Invalid user_id '%s'", user_id)
            return RateLimitResult(
                allowed=False,
                limit_reached=True,
                limit_scope="user",
                message="Invalid user identification. Please log in again.",
            )

        # Count successful user generations since midnight UTC of current day
        now = datetime.now(timezone.utc)
        midnight_utc = datetime(
            now.year, now.month, now.day, tzinfo=timezone.utc
        )

        query = {
            "user_id": user_oid,
            "status": "success",
            "prompt_used": {"$ne": "(served from cache)"},
            "created_at": {"$gte": midnight_utc},
        }
        try:
            count = col.count_documents(query)
            if count >= AI_MAX_GENERATIONS_PER_USER_PER_DAY:
                logger.info(
                    "[rate_limit] User %s hit limit: %d/%d",
                    user_id,
                    count,
                    AI_MAX_GENERATIONS_PER_USER_PER_DAY,
                )
                return RateLimitResult(
                    allowed=False,
                    limit_reached=True,
                    limit_scope="user",
                    message=(
                        f"You have reached the limit of {AI_MAX_GENERATIONS_PER_USER_PER_DAY} "
                        "previews per day. Please try again tomorrow."
                    ),
                )
            logger.debug(
                "[rate_limit] User %s count: %d/%d",
                user_id,
                count,
                AI_MAX_GENERATIONS_PER_USER_PER_DAY,
            )
        except Exception as exc:
            logger.error("[rate_limit] DB error during user count: %s. Failing closed.", exc)
            return RateLimitResult(
                allowed=False,
                limit_reached=True,
                limit_scope="user",
                message="Rate limiting service is temporarily unavailable. Please try again later.",
            )

    # 2. Guest limit check (Lifetime per session_id)
    else:
        query = {
            "session_id": session_id,
            "user_id": None,
            "status": "success",
            "prompt_used": {"$ne": "(served from cache)"},
        }
        try:
            count = col.count_documents(query)
            if count >= AI_FREE_GENERATIONS_PER_SESSION:
                logger.info(
                    "[rate_limit] Guest session %s hit limit: %d/%d",
                    session_id,
                    count,
                    AI_FREE_GENERATIONS_PER_SESSION,
                )
                return RateLimitResult(
                    allowed=False,
                    limit_reached=True,
                    limit_scope="guest",
                    message="Sign up to keep designing",
                )
            logger.debug(
                "[rate_limit] Guest session %s count: %d/%d",
                session_id,
                count,
                AI_FREE_GENERATIONS_PER_SESSION,
            )
        except Exception as exc:
            logger.error("[rate_limit] DB error during guest count: %s. Failing closed.", exc)
            return RateLimitResult(
                allowed=False,
                limit_reached=True,
                limit_scope="guest",
                message="Rate limiting service is temporarily unavailable. Please try again later.",
            )

    return RateLimitResult(
        allowed=True,
        limit_reached=False,
        limit_scope="",
        message="",
    )


def increment_usage(session_id: str, user_id: str | None) -> None:
    """
    Since usage is calculated dynamically by counting entries in the
    'ai_generations' collection, we do not need to keep separate state counters.
    This function is kept for backward compatibility and is a clean no-op.
    """
    pass
>>>>>>> origin/main
