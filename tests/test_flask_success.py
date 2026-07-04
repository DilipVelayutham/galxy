import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from app import create_app

class TestFlaskSuccess(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.category_id = "66851234af504e44a4b8c771"

    @patch("app.db")
    @patch("app.models.ai_generation.AIGeneration.get_collection")
    @patch("app.services.ai_service.check_rate_limit")
    @patch("app.services.ai_service.check_cache")
    @patch("app.services.ai_service.upload_to_cloudinary")
    def test_post_preview_success(self, mock_upload, mock_cache, mock_rate, mock_get_col, mock_db):
        # Mock database category resolution
        mock_db["categories"].find_one.return_value = {
            "_id": ObjectId(self.category_id),
            "name": "Neon Sign",
            "ai_prompt_template": "Neon Sign in {color}",
            "attributes": [
                {"key": "color", "affects_ai_preview": True, "options": [{"code": "blue", "label": "blue"}]}
            ]
        }
        
        mock_rate.return_value = {"allowed": True, "limit_reached": False, "limit_scope": None}
        mock_cache.return_value = {"hit": False, "output_image_url": None}
        mock_upload.return_value = "https://cloudinary.com/uploaded.png"
        
        mock_insert = MagicMock()
        mock_insert.inserted_id = ObjectId("66851234af504e44a4b8c777")
        mock_get_col.return_value.insert_one.return_value = mock_insert
        
        payload = {
            "category_id": self.category_id,
            "session_id": "test-session-uuid",
            "selected_attributes": {
                "color": "blue"
            }
        }
        
        r = self.client.post("/api/ai/generate-preview", json=payload)
        
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json["success"])
        self.assertEqual(r.json["data"]["output_image_url"], "https://cloudinary.com/uploaded.png")
        self.assertFalse(r.json["data"]["from_cache"])
        self.assertEqual(r.json["data"]["generation_id"], "66851234af504e44a4b8c777")
