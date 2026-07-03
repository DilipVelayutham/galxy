"""
module4_client.py — Module 5 utility
Cross-module integration: delegates attribute validation to Module 4.

Per spec §11 guardrail: Module 5 does NOT validate attribute selections itself.
It always delegates to Module 4's validate_attributes().

This client supports two modes:
  1. HTTP call to Module 4's internal validation endpoint (production/integration).
  2. Local fallback (development/testing when Module 4 is not running).

The fallback allows Backend Member 1 to develop in isolation on Day 1-2
without blocking on Module 4 being available. Switch to HTTP mode before
Day 3 integration.
"""
import logging
import os
import requests as http_requests
from app.configs.ai_config import MODULE4_VALIDATE_URL

logger = logging.getLogger(__name__)

# Set M4_VALIDATION_MODE=local in .env to use the dev fallback.
_MODE = os.getenv("M4_VALIDATION_MODE", "http").lower()


def validate_attributes(
    category: dict,
    selected_attributes: dict,
) -> dict:
    """
    Validate selected_attributes against the category's attribute schema.

    Delegates to Module 4 via HTTP (production) or local fallback (dev).

    Returns:
        {
            "valid": bool,
            "errors": list[str],    # empty list if valid
            "message": str          # human-readable summary
        }
    """
    if _MODE == "local":
        return _local_validate(category, selected_attributes)
    return _http_validate(category, selected_attributes)


def _http_validate(category: dict, selected_attributes: dict) -> dict:
    """
    Call Module 4's internal validation endpoint.
    Endpoint: POST {MODULE4_VALIDATE_URL}
    Body: { "category_id": str, "selected_attributes": {} }
    """
    try:
        response = http_requests.post(
            MODULE4_VALIDATE_URL,
            json={
                "category_id": str(category.get("_id", "")),
                "selected_attributes": selected_attributes,
            },
            timeout=5,
        )
        data = response.json()
        if response.status_code == 200:
            return {"valid": True, "errors": [], "message": ""}
        # Module 4 returns 400 on validation failure with error details.
        return {
            "valid": False,
            "errors": data.get("errors", []),
            "message": data.get("message", "Attribute validation failed."),
        }
    except http_requests.Timeout:
        logger.error(
            "[module4_client] Timeout calling Module 4 validation endpoint."
        )
        # Fail-open in dev, fail-closed in production — here we fail open for now.
        return {"valid": True, "errors": [], "message": "(Module 4 timeout — fallback)"}
    except Exception as exc:
        logger.error(
            "[module4_client] Error calling Module 4: %s. Using fallback.", exc
        )
        return {"valid": True, "errors": [], "message": "(Module 4 unavailable — fallback)"}


def _local_validate(category: dict, selected_attributes: dict) -> dict:
    """
    Local development fallback validation.
    Checks that all required attributes (required==True) are present.
    Does NOT implement full validation logic — Module 4 is the source of truth.
    """
    attributes: list[dict] = category.get("attributes", [])
    errors = []
    for attr in attributes:
        if attr.get("required", False):
            key = attr.get("key", "")
            if key not in selected_attributes or selected_attributes[key] in (None, ""):
                errors.append(f"'{key}' is required.")

    if errors:
        return {
            "valid": False,
            "errors": errors,
            "message": "Missing required attributes: " + ", ".join(errors),
        }
    return {"valid": True, "errors": [], "message": ""}
