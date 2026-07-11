"""
ai_cache_service.py — Module 5 AI Preview Generation
Deterministic hashing + cache lookup/store for generated images.
"""
import hashlib
import json
import logging
from datetime import datetime, timezone
from bson import ObjectId
from app.database import ai_cache

logger = logging.getLogger(__name__)


def _get_collection():
    """Return the MongoDB cache collection client."""
    return ai_cache


def _resolve_category_id(category_or_id) -> str:
    """Helper to extract a string ID from category dict or raw ID."""
    if isinstance(category_or_id, dict):
        return str(category_or_id.get("_id") or category_or_id.get("category_id", ""))
    return str(category_or_id)


# ─── Public Interface ─────────────────────────────────────────────────────────────

def has_custom_text(selected_attributes: dict, category: dict) -> bool:
    """
    Check if the user configuration contains any custom/free-text attribute value.
    If so, cache lookup must be bypassed (spec §7).
    """
    attributes = category.get("attributes") or category.get("attribute_schema") or []
    text_keys = {attr["key"] for attr in attributes if attr.get("type") in ("text", "text_input")}
    
    # Always treat 'custom_text' as a free-text field
    text_keys.add("custom_text")

    for key, val in selected_attributes.items():
        if key in text_keys and str(val).strip():
            return True
        # Heuristic fallback for any key containing 'text'
        if "text" in key.lower() and str(val).strip():
            return True

    return False


def is_cache_bypassed(category_or_id, selected_attributes: dict) -> bool:
    """Legacy wrapper for has_custom_text (HEAD)."""
    if isinstance(category_or_id, dict):
        return has_custom_text(selected_attributes, category_or_id)
    # If only ID is provided, we check against standard keys
    text_keys = {"custom_text"}
    for key, val in selected_attributes.items():
        if (key in text_keys or "text" in key.lower()) and str(val).strip():
            return True
    return False


def check_cache(category_or_id, selected_attributes: dict) -> str | None:
    """
    Query MongoDB for a cached preview URL.
    Returns the secure URL on cache hit, or None on cache miss.
    """
    if is_cache_bypassed(category_or_id, selected_attributes):
        logger.info("[Cache] BYPASS (custom text detected)")
        return None

    category_id = _resolve_category_id(category_or_id)
    cache_key = make_cache_key(category_id, selected_attributes)
    col = _get_collection()

    try:
        entry = col.find_one({"_id": cache_key})
        if entry:
            logger.info("[Cache] HIT for key: %s", cache_key)
            return entry.get("output_image_url")
        logger.info("[Cache] MISS for key: %s", cache_key)
        return None
    except Exception as exc:
        logger.error("[Cache] Failed to read from cache: %s", exc)
        return None


def store_cache(category_or_id, selected_attributes: dict, output_image_url: str) -> None:
    """
    Store a configuration mapping in the DB cache collection.
    Upserts using the deterministic cache key as the document _id.
    """
    category_id = _resolve_category_id(category_or_id)
    cache_key = make_cache_key(category_id, selected_attributes)
    col = _get_collection()

    try:
        col.update_one(
            {"_id": cache_key},
            {
                "$set": {
                    "category_id": ObjectId(category_id) if len(category_id) == 24 else category_id,
                    "selected_attributes": selected_attributes,
                    "output_image_url": output_image_url,
                    "created_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )
        logger.info("[Cache] Stored key: %s", cache_key)
    except Exception as exc:
        logger.error("[Cache] Failed to write cache: %s", exc)


def make_cache_key(category_id: str, selected_attributes: dict) -> str:
    """
    Generate a deterministic SHA256 key for cache lookups (spec §7).
    Clean keys and sort alphabetically to prevent key-order mismatch.
    """
    # Clean selected_attributes to remove None or empty values
    cleaned = {}
    for k in sorted(selected_attributes.keys()):
        val = selected_attributes[k]
        if val is not None and str(val).strip():
            cleaned[k] = val

    sorted_attrs = json.dumps(cleaned, sort_keys=True)
    raw = f"{category_id}:{sorted_attrs}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def generate_cache_key(category_or_id, selected_attributes: dict) -> str:
    """Legacy wrapper for make_cache_key (HEAD)."""
    category_id = _resolve_category_id(category_or_id)
    return make_cache_key(category_id, selected_attributes)

