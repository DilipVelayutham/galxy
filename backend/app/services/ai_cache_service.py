"""
ai_cache_service.py — Module 5 AI Preview Generation
Deterministic hashing + cache lookup/store for generated images.

Maintains an 'ai_caches' collection in MongoDB to save costs and avoid
redundant generations for duplicate configurations.
"""
import hashlib
import json
import logging
from datetime import datetime, timezone
from app.db import get_db

logger = logging.getLogger(__name__)


def _get_collection():
    """Return the ai_caches collection from MongoDB database."""
    return get_db()["ai_caches"]


def check_cache(category_id: str, selected_attributes: dict) -> str | None:
    """
    Look up a previously generated image URL for this exact configuration.

    Args:
        category_id: string ObjectId of the category.
        selected_attributes: the validated attribute selections.

    Returns:
        A Cloudinary output_image_url if a cached hit exists, else None.
    """
    cache_key = make_cache_key(category_id, selected_attributes)
    try:
        entry = _get_collection().find_one({"_id": cache_key})
        if entry:
            logger.info("[cache] HIT for cache key %s", cache_key)
            return entry.get("output_image_url")
    except Exception as exc:
        logger.warning("[cache] Error reading from cache database: %s", exc)

    logger.debug("[cache] MISS for cache key %s", cache_key)
    return None


def store_cache(
    category_id: str,
    selected_attributes: dict,
    output_image_url: str,
) -> None:
    """
    Store the generated image URL for this configuration.

    Args:
        category_id: string ObjectId of the category.
        selected_attributes: the validated attribute selections.
        output_image_url: the Cloudinary URL of the generated image.
    """
    if not output_image_url:
        return

    cache_key = make_cache_key(category_id, selected_attributes)
    try:
        _get_collection().update_one(
            {"_id": cache_key},
            {
                "$set": {
                    "category_id": category_id,
                    "selected_attributes": selected_attributes,
                    "output_image_url": output_image_url,
                    "created_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )
        logger.info("[cache] Cached entry successfully for key %s", cache_key)
    except Exception as exc:
        logger.warning("[cache] Error writing to cache database: %s", exc)


def has_custom_text(selected_attributes: dict, category: dict) -> bool:
    """
    Returns True if any of the selected attributes is a free-text / custom_text
    type that makes this generation unique — in which case caching must be bypassed.

    Per spec §7: "Only bypass cache when custom_text (or any customer-specific
    free text) is part of selected_attributes."
    """
    attributes: list[dict] = category.get("attributes", [])
    attr_schema_map = {a["key"]: a for a in attributes}

    for key in selected_attributes:
        schema = attr_schema_map.get(key, {})
        attr_type = schema.get("type", "option")
        if attr_type in ("text", "text_input", "custom_text"):
            return True
    return False


def make_cache_key(category_id: str, selected_attributes: dict) -> str:
    """
    Build a deterministic cache key string from category_id + sorted attributes.
    Uses SHA256 of the JSON representation of sorted key-values.
    """
    # Sort the dictionary keys and dump to JSON string for stable output
    sorted_attrs = json.dumps(selected_attributes, sort_keys=True)
    raw = f"{category_id}:{sorted_attrs}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
