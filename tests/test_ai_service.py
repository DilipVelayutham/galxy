import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from app.services.ai_service import orchestrate_generation

class TestAIService(unittest.TestCase):
    def setUp(self):
        self.category_id = "66851234af504e44a4b8c771"
        self.category = {
            "_id": ObjectId(self.category_id),
            "name": "Neon Sign",
            "ai_prompt_template": "A neon sign spelling {custom_text} in {color}",
            "attributes": [
                {"key": "color", "affects_ai_preview": True, "options": [{"code": "blue", "label": "blue"}]},
                {"key": "custom_text", "type": "text", "affects_ai_preview": True}
            ]
        }
        self.selected_attributes = {
            "color": "blue",
            "custom_text": "Hello"
        }
        
    @patch("app.db")
    @patch("app.models.ai_generation.AIGeneration.get_collection")
    @patch("app.services.ai_service.check_rate_limit")
    @patch("app.services.ai_service.check_cache")
    @patch("app.services.ai_service.generate_image")
    @patch("app.services.ai_service.upload_to_cloudinary")
    def test_orchestrate_success(self, mock_upload, mock_generate, mock_cache, mock_rate, mock_get_col, mock_db):
        # Mock database category find
        mock_db["categories"].find_one.return_value = self.category
        
        # Mock dependencies (rate limits allowed, cache missed, provider succeeds)
        mock_rate.return_value = {"allowed": True, "limit_reached": False, "limit_scope": None}
        mock_cache.return_value = {"hit": False, "output_image_url": None}
        mock_generate.return_value = {"success": True, "image_bytes": b"fake_bytes", "error": None}
        mock_upload.return_value = "https://cloudinary.com/fake.png"
        
        mock_insert = MagicMock()
        mock_insert.inserted_id = ObjectId("66851234af504e44a4b8c772")
        mock_get_col.return_value.insert_one.return_value = mock_insert
        
        result = orchestrate_generation(
            category_id=self.category_id,
            product_id=None,
            selected_attributes=self.selected_attributes,
            session_id="session-123",
            user_id=None
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["data"]["output_image_url"], "https://cloudinary.com/fake.png")
        self.assertFalse(result["data"]["from_cache"])
        
        # Verify database logs
        mock_get_col.return_value.insert_one.assert_called_once()
        inserted_record = mock_get_col.return_value.insert_one.call_args[0][0]
        self.assertEqual(inserted_record["status"], "success")
        self.assertEqual(inserted_record["output_image_url"], "https://cloudinary.com/fake.png")
        
    @patch("app.db")
    @patch("app.models.ai_generation.AIGeneration.get_collection")
    @patch("app.services.ai_service.check_rate_limit")
    def test_orchestrate_rate_limited(self, mock_rate, mock_get_col, mock_db):
        mock_db["categories"].find_one.return_value = self.category
        mock_rate.return_value = {"allowed": False, "limit_reached": True, "limit_scope": "session"}
        
        mock_insert = MagicMock()
        mock_insert.inserted_id = ObjectId("66851234af504e44a4b8c773")
        mock_get_col.return_value.insert_one.return_value = mock_insert
        
        result = orchestrate_generation(
            category_id=self.category_id,
            product_id=None,
            selected_attributes=self.selected_attributes,
            session_id="session-123",
            user_id=None
        )
        
        self.assertFalse(result["success"])
        self.assertEqual(result["status_code"], 429)
        self.assertTrue(result["data"]["limit_reached"])
        self.assertEqual(result["data"]["limit_scope"], "session")
        
        # Verify database logs
        mock_get_col.return_value.insert_one.assert_called_once()
        inserted_record = mock_get_col.return_value.insert_one.call_args[0][0]
        self.assertEqual(inserted_record["status"], "rate_limited")
        
    @patch("app.db")
    @patch("app.models.ai_generation.AIGeneration.get_collection")
    @patch("app.services.ai_service.check_rate_limit")
    @patch("app.services.ai_service.check_cache")
    def test_orchestrate_cache_hit(self, mock_cache, mock_rate, mock_get_col, mock_db):
        mock_db["categories"].find_one.return_value = self.category
        mock_rate.return_value = {"allowed": True, "limit_reached": False, "limit_scope": None}
        mock_cache.return_value = {"hit": True, "output_image_url": "https://cloudinary.com/cached.png"}
        
        mock_insert = MagicMock()
        mock_insert.inserted_id = ObjectId("66851234af504e44a4b8c774")
        mock_get_col.return_value.insert_one.return_value = mock_insert
        
        result = orchestrate_generation(
            category_id=self.category_id,
            product_id=None,
            selected_attributes=self.selected_attributes,
            session_id="session-123",
            user_id=None
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["data"]["output_image_url"], "https://cloudinary.com/cached.png")
        self.assertTrue(result["data"]["from_cache"])
        
        inserted_record = mock_get_col.return_value.insert_one.call_args[0][0]
        self.assertEqual(inserted_record["status"], "success")
        self.assertEqual(inserted_record["generation_time_ms"], 0)
