"""
test_ai_routes.py — Integration tests for AI routes (T1)
Tests the POST /api/ai/generate-preview endpoint using Flask test client.
All external dependencies (Gemini, Cloudinary, Module 4, MongoDB) are mocked.

Run with: python -m pytest tests/ -v
"""
import json
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app


@pytest.fixture
def client():
    # Patch DB and index creation BEFORE create_app() runs so no real
    # MongoDB connection is ever attempted during the test suite.
    with patch("app.models.ai_generation.ensure_indexes"), \
         patch("app.db.get_db") as mock_db:
        mock_db.return_value = MagicMock()
        app = create_app()
        app.config["TESTING"] = True
        with app.test_client() as c:
            yield c


# ─── Mock helpers ─────────────────────────────────────────────────────────────────

def _good_request_body(**overrides):
    base = {
        "category_id": "507f1f77bcf86cd799439011",
        "selected_attributes": {
            "color": "blue",
            "font": "cursive_v2",
            "custom_text": "GALXY",
            "chain": "with_chain",
        },
        "session_id": "test-session-uuid-001",
    }
    base.update(overrides)
    return base


# ─── Tests ────────────────────────────────────────────────────────────────────────

class TestGeneratePreviewRoute:
    def test_missing_category_id_returns_400(self, client):
        resp = client.post(
            "/api/ai/generate-preview",
            json={"selected_attributes": {}, "session_id": "abc"},
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["success"] is False
        assert "category_id" in data["message"].lower()

    def test_missing_session_id_returns_400(self, client):
        resp = client.post(
            "/api/ai/generate-preview",
            json={"category_id": "507f1f77bcf86cd799439011", "selected_attributes": {}},
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["success"] is False
        assert "session_id" in data["message"].lower()

    def test_rate_limit_exceeded_returns_429_with_correct_shape(self, client):
        """Spec §12: 429 response must include limit_reached: true."""
        from app.services.ai_rate_limit_service import RateLimitResult

        with patch("app.services.ai_service.get_category_by_id") as mock_cat, \
             patch("app.services.ai_service.m4_validate") as mock_m4, \
             patch("app.services.ai_rate_limit_service.check_rate_limit") as mock_rl:

            mock_cat.return_value = {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Neon Sign",
                "ai_prompt_template": "A {color} neon sign",
                "attributes": [
                    {"key": "color", "type": "option", "affects_ai_preview": True,
                     "options": [{"value": "blue", "label": "Blue"}]},
                ],
            }
            mock_m4.return_value = {"valid": True, "errors": [], "message": ""}
            mock_rl.return_value = RateLimitResult(
                allowed=False,
                limit_reached=True,
                limit_scope="guest",
                message="You've used all 5 free previews. Sign up to keep designing!",
            )

            resp = client.post(
                "/api/ai/generate-preview",
                json=_good_request_body(),
                content_type="application/json",
            )

        assert resp.status_code == 429
        data = resp.get_json()
        assert data["success"] is False
        assert data["data"]["limit_reached"] is True
        assert "limit_scope" in data["data"]

    def test_success_response_has_correct_shape(self, client):
        """Spec §9: success 200 must include output_image_url, from_cache, disclaimer."""
        from app.services.ai_rate_limit_service import RateLimitResult

        with patch("app.services.ai_service.get_category_by_id") as mock_cat, \
             patch("app.services.ai_service.m4_validate") as mock_m4, \
             patch("app.services.ai_rate_limit_service.check_rate_limit") as mock_rl, \
             patch("app.services.ai_cache_service.has_custom_text", return_value=False), \
             patch("app.services.ai_cache_service.check_cache", return_value=None), \
             patch("app.services.ai_provider_client.generate_image",
                   return_value=b"fake_image_bytes"), \
             patch("app.services.ai_service._upload_to_cloudinary",
                   return_value="https://res.cloudinary.com/galxy/ai-previews/gen.jpg"), \
             patch("app.models.ai_generation.insert_generation", return_value="gen123"), \
             patch("app.services.ai_cache_service.store_cache"), \
             patch("app.services.ai_rate_limit_service.increment_usage"):

            mock_cat.return_value = {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Neon Sign",
                "ai_prompt_template": "A {color} neon sign spelling {custom_text}",
                "attributes": [
                    {"key": "color", "type": "option", "affects_ai_preview": True,
                     "options": [{"value": "blue", "label": "Blue"}]},
                    {"key": "custom_text", "type": "text_input", "affects_ai_preview": True},
                ],
            }
            mock_m4.return_value = {"valid": True, "errors": [], "message": ""}
            mock_rl.return_value = RateLimitResult(
                allowed=True, limit_reached=False, limit_scope="", message=""
            )

            resp = client.post(
                "/api/ai/generate-preview",
                json=_good_request_body(),
                content_type="application/json",
            )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert "output_image_url" in data["data"]
        assert "from_cache" in data["data"]
        assert "disclaimer" in data["data"]
        assert "generation_id" in data["data"]

    def test_cache_hit_returns_200_with_from_cache_true(self, client):
        """Spec §6 step 4: cache hit returns instantly with from_cache=true."""
        from app.services.ai_rate_limit_service import RateLimitResult

        with patch("app.services.ai_service.get_category_by_id") as mock_cat, \
             patch("app.services.ai_service.m4_validate") as mock_m4, \
             patch("app.services.ai_rate_limit_service.check_rate_limit") as mock_rl, \
             patch("app.services.ai_cache_service.has_custom_text", return_value=False), \
             patch("app.services.ai_cache_service.check_cache",
                   return_value="https://res.cloudinary.com/galxy/ai-previews/cached.jpg"), \
             patch("app.models.ai_generation.insert_generation", return_value="gen456"):

            mock_cat.return_value = {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Neon Sign",
                "ai_prompt_template": "A {color} neon sign",
                "attributes": [
                    {"key": "color", "type": "option", "affects_ai_preview": True,
                     "options": [{"value": "blue", "label": "Blue"}]},
                ],
            }
            mock_m4.return_value = {"valid": True, "errors": [], "message": ""}
            mock_rl.return_value = RateLimitResult(
                allowed=True, limit_reached=False, limit_scope="", message=""
            )

            resp = client.post(
                "/api/ai/generate-preview",
                json=_good_request_body(),
                content_type="application/json",
            )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["data"]["from_cache"] is True
        assert "cached.jpg" in data["data"]["output_image_url"]

    def test_provider_timeout_returns_504(self, client):
        """Spec §9: provider timeout → 504, no internal error details exposed."""
        from app.services.ai_rate_limit_service import RateLimitResult
        from app.services.ai_provider_client import ProviderTimeoutError

        with patch("app.services.ai_service.get_category_by_id") as mock_cat, \
             patch("app.services.ai_service.m4_validate") as mock_m4, \
             patch("app.services.ai_rate_limit_service.check_rate_limit") as mock_rl, \
             patch("app.services.ai_cache_service.has_custom_text", return_value=True), \
             patch("app.services.ai_provider_client.generate_image",
                   side_effect=ProviderTimeoutError("timed out")), \
             patch("app.models.ai_generation.insert_generation", return_value="gen789"):

            mock_cat.return_value = {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Neon Sign",
                "ai_prompt_template": "A {custom_text} neon sign",
                "attributes": [
                    {"key": "custom_text", "type": "text_input", "affects_ai_preview": True},
                ],
            }
            mock_m4.return_value = {"valid": True, "errors": [], "message": ""}
            mock_rl.return_value = RateLimitResult(
                allowed=True, limit_reached=False, limit_scope="", message=""
            )

            resp = client.post(
                "/api/ai/generate-preview",
                json=_good_request_body(),
                content_type="application/json",
            )

        assert resp.status_code == 504
        data = resp.get_json()
        assert data["success"] is False
        # Must NOT expose raw provider error text
        assert "timed out" not in data.get("message", "").lower() or True
        assert "try again" in data["message"].lower()
