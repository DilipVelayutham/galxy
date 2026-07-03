"""
ai_rate_limit_service.py — Module 5 AI Preview Generation (T4 — Backend Member 2)
Two-tier rate limiting: guest (session_id) + logged-in user (daily cap).

OWNER: Gokul B (Backend Member 2, feat-m5-t3-rate-limiting)
This file is a stub interface contract from Backend Member 1's perspective.
Backend Member 2 will provide the full implementation in their branch.

Interface contract (frozen from Day 1 per spec §12):
  check_rate_limit(session_id, user_id) → RateLimitResult

Per spec §8:
  - Guest (session_id): AI_FREE_GENERATIONS_PER_SESSION total across all time.
  - Logged-in (user_id): AI_MAX_GENERATIONS_PER_USER_PER_DAY, resets daily.
  - Cached hits do NOT count against limits (only new provider calls).
"""
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RateLimitResult:
    """
    Result of a rate-limit check.
    Fields match the 429 response shape required by the frontend (spec §9, §12).
    """
    allowed: bool
    limit_reached: bool
    limit_scope: str   # "guest" | "user" | ""   (empty when allowed)
    message: str       # human-readable message for the frontend upsell UI


def check_rate_limit(session_id: str, user_id: str | None) -> RateLimitResult:
    """
    Check whether this session/user may trigger a new AI generation.

    Per spec §8: cached hits should NOT call this function — only new
    provider calls consume quota. The caller (ai_service.py) is responsible
    for calling check_cache() first, and only calling check_rate_limit()
    when a genuine new generation will occur.

    Args:
        session_id: always present (guest UUID or logged-in user's session).
        user_id: string ObjectId if logged in, None if guest.

    Returns:
        RateLimitResult with .allowed == True if generation may proceed.
    """
    # STUB — Backend Member 2 will implement with MongoDB counters.
    # For now, always allow so Backend Member 1's orchestration can be tested.
    logger.debug(
        "[rate_limit] check called session=%s user=%s (stub — always allows)",
        session_id,
        user_id,
    )
    return RateLimitResult(
        allowed=True,
        limit_reached=False,
        limit_scope="",
        message="",
    )


def increment_usage(session_id: str, user_id: str | None) -> None:
    """
    Increment the usage counter for this session/user after a successful
    (non-cached) generation.

    STUB — Backend Member 2 will implement.
    """
    logger.debug(
        "[rate_limit] increment_usage called session=%s user=%s (stub — no-op)",
        session_id,
        user_id,
    )
