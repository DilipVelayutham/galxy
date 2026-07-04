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
