"""
ai_cache_service.py — Module 5 AI Preview Generation (T3 — Backend Member 2)
Deterministic hashing + cache lookup/store for generated images.

OWNER: Gokul B (Backend Member 2, feat-m5-t3-rate-limiting)
This file is a stub interface contract from Backend Member 1's perspective.
Backend Member 2 will provide the full implementation in their branch.

Interface contract (frozen from Day 1 per spec §12):
  check_cache(category_id, selected_attributes) → str | None
  store_cache(category_id, selected_attributes, output_image_url) → None

The cache key is a deterministic hash of category_id + sorted(selected_attributes).
custom_text / text_input fields always BYPASS the cache (each is unique).
"""
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def check_cache(category_id: str, selected_attributes: dict) -> str | None:
    """
    Look up a previously generated image URL for this exact configuration.

    Args:
        category_id: string ObjectId of the category.
        selected_attributes: the validated attribute selections.

    Returns:
        A Cloudinary output_image_url if a cached hit exists, else None.
    """
    # STUB — Backend Member 2 will implement with MongoDB / Redis lookup.
    # During integration, replace this return None with the real lookup.
    logger.debug(
        "[cache] check_cache called for category=%s (stub — returns None)",
        category_id,
    )
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
    # STUB — Backend Member 2 will implement with MongoDB / Redis upsert.
    logger.debug(
        "[cache] store_cache called for category=%s (stub — no-op)",
        category_id,
    )


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
    Public so Backend Member 2 can reuse the same key logic in their store/lookup.
    """
    sorted_attrs = json.dumps(selected_attributes, sort_keys=True)
    raw = f"{category_id}:{sorted_attrs}"
    return hashlib.sha256(raw.encode()).hexdigest()
