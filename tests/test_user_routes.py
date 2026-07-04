import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from datetime import datetime, timezone
from app import create_app

class TestUserRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.user_id = "66851234af504e44a4b8c775"
        self.other_user_id = "66851234af504e44a4b8c776"

    @patch("app.models.ai_generation.AIGeneration.get_collection")
    def test_user_history_unauthorized(self, mock_get_col):
        # Omit authentication headers entirely
        r = self.client.get(f"/api/ai/generations/{self.user_id}")
        self.assertEqual(r.status_code, 401)
        self.assertFalse(r.json["success"])

    @patch("app.models.ai_generation.AIGeneration.get_collection")
    def test_user_history_forbidden(self, mock_get_col):
        # Call User A's history passing User B's X-User-Id
        headers = {"X-User-Id": self.other_user_id}
        r = self.client.get(f"/api/ai/generations/{self.user_id}", headers=headers)
        self.assertEqual(r.status_code, 403)
        self.assertFalse(r.json["success"])

    @patch("app.models.ai_generation.AIGeneration.get_collection")
    def test_user_history_success_authorized(self, mock_get_col):
        headers = {"X-User-Id": self.user_id}
        
        # Mock database cursor return values
        fake_id = ObjectId("66851234af504e44a4b8c772")
        mock_get_col.return_value.find.return_value.sort.return_value.skip.return_value.limit.return_value = [
            {
                "_id": fake_id,
                "user_id": ObjectId(self.user_id),
                "category_id": ObjectId("66851234af504e44a4b8c771"),
                "status": "success",
                "created_at": datetime.now(timezone.utc)
            }
        ]
        mock_get_col.return_value.count_documents.return_value = 1
        
        # Valid user requesting their own history
        r = self.client.get(f"/api/ai/generations/{self.user_id}", headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json["success"])
        self.assertEqual(len(r.json["data"]["generations"]), 1)
        self.assertEqual(r.json["data"]["generations"][0]["user_id"], self.user_id)

    @patch("app.models.ai_generation.AIGeneration.get_collection")
    def test_user_history_success_admin(self, mock_get_col):
        # Admin request for User A's history
        headers = {"X-Admin-Role": "admin"}
        
        mock_get_col.return_value.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
        mock_get_col.return_value.count_documents.return_value = 0
        
        r = self.client.get(f"/api/ai/generations/{self.user_id}", headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json["success"])
