"""
ai_rate_limit_service.py — Module 5 AI Preview Generation
Two-tier rate limiting: guest (session_id) + logged-in user (daily cap).
"""
import logging
from datetime import datetime, timezone
from bson import ObjectId
from app.db import get_db
from app.configs.ai_config import (
    AI_FREE_GENERATIONS_PER_SESSION,
    AI_MAX_GENERATIONS_PER_USER_PER_DAY,
)

logger = logging.getLogger(__name__)


# ─── Structured Rate Limit Result with Dict Compatibility ────────────────────────────

class RateLimitResult:
    """
    Result of a rate-limit check.
    Behaves as both a dataclass-like object and a dictionary for backward compatibility.
    """
    def __init__(self, allowed: bool, limit_reached: bool, limit_scope: str, message: str = ""):
        self.allowed = allowed
        self.limit_reached = limit_reached
        self.limit_scope = limit_scope   # "guest" | "user" | ""
        self.message = message

    def __getitem__(self, key):
        if key == "allowed":
            return self.allowed
        if key == "limit_reached":
            return self.limit_reached
        if key == "limit_scope":
            return self.limit_scope
        if key == "message":
            return self.message
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


def _get_generations_collection():
    """Return the ai_generations collection from MongoDB."""
    return get_db()["ai_generations"]


def check_rate_limit(
    session_id: str = None,
    user_id: str | None = None,
    ip_address: str | None = None,
    **kwargs
) -> RateLimitResult:
    """
    Check whether this session/user may trigger a new AI generation.
    Supports both keyword styles and fallbacks.
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

    # 2. Guest limit check (Lifetime per session_id + rolling 24h per IP address)
    else:
        # Check IP address limit first if available
        if ip_address:
            from datetime import timedelta
            twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
            ip_query = {
                "ip_address": ip_address,
                "user_id": None,
                "status": "success",
                "prompt_used": {"$ne": "(served from cache)"},
                "created_at": {"$gte": twenty_four_hours_ago},
            }
            try:
                ip_count = col.count_documents(ip_query)
                if ip_count >= AI_FREE_GENERATIONS_PER_SESSION:
                    logger.info(
                        "[rate_limit] IP %s hit limit: %d/%d",
                        ip_address,
                        ip_count,
                        AI_FREE_GENERATIONS_PER_SESSION,
                    )
                    return RateLimitResult(
                        allowed=False,
                        limit_reached=True,
                        limit_scope="guest",
                        message="Sign up to keep designing",
                    )
            except Exception as exc:
                logger.error("[rate_limit] DB error during IP count: %s. Failing closed.", exc)
                return RateLimitResult(
                    allowed=False,
                    limit_reached=True,
                    limit_scope="guest",
                    message="Rate limiting service is temporarily unavailable. Please try again later.",
                )

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

