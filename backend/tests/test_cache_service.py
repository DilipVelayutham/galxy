"""
test_cache_service.py — Unit tests for ai_cache_service (T3)
All external dependencies (MongoDB) are mocked.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.ai_cache_service import (
    make_cache_key,
    has_custom_text,
    check_cache,
    store_cache,
)

# ─── Fixture Data ─────────────────────────────────────────────────────────────

NEON_CATEGORY = {
    "_id": "507f1f77bcf86cd799439011",
    "name": "Neon Sign",
    "attributes": [
        {"key": "color", "type": "option", "affects_ai_preview": True},
        {"key": "font", "type": "option", "affects_ai_preview": True},
        {"key": "custom_text", "type": "text_input", "affects_ai_preview": True},
    ],
}

LED_CATEGORY = {
    "_id": "507f1f77bcf86cd799439022",
    "name": "LED Letter Sign",
    "attributes": [
        {"key": "size", "type": "option", "affects_ai_preview": True},
        {"key": "finish", "type": "option", "affects_ai_preview": True},
    ],
}


# ─── Tests ────────────────────────────────────────────────────────────────────

class TestCacheService:
    def test_make_cache_key_is_deterministic_and_sorted(self):
        """Spec §7: Cache key must be stable and sort selected_attributes keys."""
        cat_id = "507f1f77bcf86cd799439011"
        attrs_a = {"color": "blue", "font": "cursive_v2"}
        attrs_b = {"font": "cursive_v2", "color": "blue"}
        
        key_a = make_cache_key(cat_id, attrs_a)
        key_b = make_cache_key(cat_id, attrs_b)
        
        # Keys must be identical regardless of input dict key order
        assert key_a == key_b
        assert len(key_a) == 64  # SHA-256 hash length in hex

    def test_has_custom_text_bypasses_correctly(self):
        """Spec §7: Cache is bypassed when custom_text is present in selected_attributes."""
        # Custom text included
        assert has_custom_text({"color": "blue", "custom_text": "GALXY"}, NEON_CATEGORY) is True
        
        # Custom text NOT included
        assert has_custom_text({"color": "blue", "font": "cursive_v2"}, NEON_CATEGORY) is False
        
        # Category has no custom text attribute (LED letter sign)
        assert has_custom_text({"size": "medium_60cm"}, LED_CATEGORY) is False

    @patch("app.services.ai_cache_service._get_collection")
    def test_check_cache_hit(self, mock_collection):
        """check_cache should return the output_image_url on DB hit."""
        mock_db = MagicMock()
        mock_collection.return_value = mock_db
        mock_db.find_one.return_value = {
            "_id": "dummy_key",
            "output_image_url": "https://cloudinary.com/cached.jpg"
        }
        
        url = check_cache("cat123", {"color": "blue"})
        assert url == "https://cloudinary.com/cached.jpg"
        mock_db.find_one.assert_called_once()

    @patch("app.services.ai_cache_service._get_collection")
    def test_check_cache_miss(self, mock_collection):
        """check_cache should return None on cache miss."""
        mock_db = MagicMock()
        mock_collection.return_value = mock_db
        mock_db.find_one.return_value = None
        
        url = check_cache("cat123", {"color": "blue"})
        assert url is None

    @patch("app.services.ai_cache_service._get_collection")
    def test_store_cache_upserts(self, mock_collection):
        """store_cache should write cache entry using update_one with upsert=True."""
        mock_db = MagicMock()
        mock_collection.return_value = mock_db
        
        store_cache("cat123", {"color": "blue"}, "https://cloudinary.com/img.jpg")
        mock_db.update_one.assert_called_once()
        args, kwargs = mock_db.update_one.call_args
        assert kwargs.get("upsert") is True
        assert args[0] == {"_id": make_cache_key("cat123", {"color": "blue"})}
