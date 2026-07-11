"""
test_rate_limit_service.py — Unit tests for ai_rate_limit_service (T3)
All external dependencies (MongoDB) are mocked.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.ai_rate_limit_service import check_rate_limit, RateLimitResult


class TestRateLimitService:
    @patch("app.services.ai_rate_limit_service._get_generations_collection")
    def test_guest_under_limit(self, mock_collection):
        """Guests under the free session cap should be allowed."""
        mock_db = MagicMock()
        mock_collection.return_value = mock_db
        # Count is 2 (limit is 5)
        mock_db.count_documents.return_value = 2

        result = check_rate_limit(session_id="session-123", user_id=None)
        assert result.allowed is True
        assert result.limit_reached is False
        mock_db.count_documents.assert_called_once()

    @patch("app.services.ai_rate_limit_service._get_generations_collection")
    def test_guest_exceeds_limit(self, mock_collection):
        """Guests exceeding the free session cap should be blocked."""
        mock_db = MagicMock()
        mock_collection.return_value = mock_db
        # Count is 5 (limit is 5)
        mock_db.count_documents.return_value = 5

        result = check_rate_limit(session_id="session-123", user_id=None)
        assert result.allowed is False
        assert result.limit_reached is True
        assert result.limit_scope == "guest"
        assert "Sign up" in result.message

    @patch("app.services.ai_rate_limit_service._get_generations_collection")
    def test_user_under_limit(self, mock_collection):
        """Logged-in users under the daily cap should be allowed."""
        mock_db = MagicMock()
        mock_collection.return_value = mock_db
        # Count is 10 (limit is 20)
        mock_db.count_documents.return_value = 10

        user_id = "507f1f77bcf86cd799439011"
        result = check_rate_limit(session_id="session-123", user_id=user_id)
        assert result.allowed is True
        assert result.limit_reached is False
        mock_db.count_documents.assert_called_once()

    @patch("app.services.ai_rate_limit_service._get_generations_collection")
    def test_user_exceeds_limit(self, mock_collection):
        """Logged-in users exceeding the daily cap should be blocked."""
        mock_db = MagicMock()
        mock_collection.return_value = mock_db
        # Count is 20 (limit is 20)
        mock_db.count_documents.return_value = 20

        user_id = "507f1f77bcf86cd799439011"
        result = check_rate_limit(session_id="session-123", user_id=user_id)
        assert result.allowed is False
        assert result.limit_reached is True
        assert result.limit_scope == "user"
        assert "reached the limit" in result.message

    @patch("app.services.ai_rate_limit_service._get_generations_collection")
    def test_db_error_fails_closed_guest(self, mock_collection):
        """DB count exceptions during guest check must fail closed (allowed=False)."""
        mock_db = MagicMock()
        mock_collection.return_value = mock_db
        mock_db.count_documents.side_effect = Exception("DB Connection Timeout")

        result = check_rate_limit(session_id="session-123", user_id=None)
        assert result.allowed is False
        assert result.limit_reached is True
        assert result.limit_scope == "guest"
        assert "temporarily unavailable" in result.message

    @patch("app.services.ai_rate_limit_service._get_generations_collection")
    def test_db_error_fails_closed_user(self, mock_collection):
        """DB count exceptions during user check must fail closed (allowed=False)."""
        mock_db = MagicMock()
        mock_collection.return_value = mock_db
        mock_db.count_documents.side_effect = Exception("DB Connection Timeout")

        user_id = "507f1f77bcf86cd799439011"
        result = check_rate_limit(session_id="session-123", user_id=user_id)
        assert result.allowed is False
        assert result.limit_reached is True
        assert result.limit_scope == "user"
        assert "temporarily unavailable" in result.message
