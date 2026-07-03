import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from datetime import datetime, timezone
from app import create_app
from app.services.ai_cache_service import check_cache
from app.services.ai_rate_limit_service import check_rate_limit

class TestCompliance(unittest.TestCase):
    def setUp(self):
        # Create a test Flask application
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        
    @patch("app.models.ai_generation.AIGeneration.get_collection")
    def test_admin_generations_auth(self, mock_get_col):
        # 1. Test unauthorized request
        r = self.client.get("/api/admin/ai/generations")
        self.assertEqual(r.status_code, 403)
        
        # 2. Test authorized request (by headers)
        headers = {"X-Admin-Role": "admin"}
        mock_get_col.return_value.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
        mock_get_col.return_value.count_documents.return_value = 0
        
        r = self.client.get("/api/admin/ai/generations", headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json["success"])

    @patch("app.models.ai_generation.AIGeneration.get_collection")
    def test_admin_generations_filtering(self, mock_get_col):
        headers = {"X-Admin-Role": "admin"}
        
        # Setup mock return values
        fake_id = ObjectId("66851234af504e44a4b8c772")
        mock_get_col.return_value.find.return_value.sort.return_value.skip.return_value.limit.return_value = [
            {
                "_id": fake_id,
                "category_id": ObjectId("66851234af504e44a4b8c771"),
                "status": "success",
                "created_at": datetime.now(timezone.utc)
            }
        ]
        mock_get_col.return_value.count_documents.return_value = 1
        
        # Request with filters
        r = self.client.get(
            "/api/admin/ai/generations?category_id=66851234af504e44a4b8c771&status=success&start_date=2026-07-01&end_date=2026-07-05",
            headers=headers
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json["data"]["generations"]), 1)
        
        # Check query parameters in count_documents call
        mock_get_col.return_value.count_documents.assert_called_once()
        query = mock_get_col.return_value.count_documents.call_args[0][0]
        self.assertEqual(query["category_id"], ObjectId("66851234af504e44a4b8c771"))
        self.assertEqual(query["status"], "success")
        self.assertIn("created_at", query)

    @patch("app.models.ai_generation.AIGeneration.get_collection")
    def test_cache_key_order_independence(self, mock_get_col):
        category_id = "66851234af504e44a4b8c771"
        
        # Setup mock db query
        mock_get_col.return_value.find_one.return_value = {"output_image_url": "https://cloudinary.com/cached.png"}
        
        # Query with color then font
        selected1 = {"color": "blue", "font": "cursive"}
        check_cache(category_id, selected1)
        
        # Verify find_one query parameters (sorted key order)
        mock_get_col.return_value.find_one.assert_called_once()
        query1 = mock_get_col.return_value.find_one.call_args[0][0]
        self.assertEqual(list(query1["selected_attributes"].keys()), ["color", "font"])
        
        mock_get_col.return_value.find_one.reset_mock()
        
        # Query with font then color
        selected2 = {"font": "cursive", "color": "blue"}
        check_cache(category_id, selected2)
        
        # Verify find_one query parameters (sorted key order remains the same!)
        mock_get_col.return_value.find_one.assert_called_once()
        query2 = mock_get_col.return_value.find_one.call_args[0][0]
        self.assertEqual(list(query2["selected_attributes"].keys()), ["color", "font"])
        self.assertEqual(query1["selected_attributes"], query2["selected_attributes"])

    @patch("app.models.ai_generation.AIGeneration.get_collection")
    def test_rate_limit_exempts_cache_hits(self, mock_get_col):
        session_id = "rate-test-session"
        
        # Setup mock count
        mock_get_col.return_value.count_documents.return_value = 0
        
        # Call rate limiter check
        check_rate_limit(user_id=None, session_id=session_id)
        
        # Verify that count_documents excludes cache hits (checks generation_time_ms > 0)
        mock_get_col.return_value.count_documents.assert_called_once()
        query = mock_get_col.return_value.count_documents.call_args[0][0]
        self.assertEqual(query["generation_time_ms"], {"$gt": 0})

    def test_caching_isolation_leak(self):
        category_id = "66851234af504e44a4b8c771"
        
        # Request A: custom_text is 'Naveen'
        selected_a = {"color": "blue", "font": "cursive", "custom_text": "Naveen"}
        cache_res_a = check_cache(category_id, selected_a)
        self.assertFalse(cache_res_a["hit"])
        
        # Request B: custom_text is 'Kumar'
        selected_b = {"color": "blue", "font": "cursive", "custom_text": "Kumar"}
        cache_res_b = check_cache(category_id, selected_b)
        self.assertFalse(cache_res_b["hit"])

    @patch("app.db")
    @patch("app.services.ai_service.check_rate_limit")
    @patch("app.models.ai_generation.AIGeneration.get_collection")
    def test_error_payload_compliance(self, mock_get_col, mock_rate, mock_db):
        mock_rate.return_value = {"allowed": False, "limit_reached": True, "limit_scope": "session"}
        mock_db["categories"].find_one.return_value = {
            "_id": ObjectId("66851234af504e44a4b8c771"),
            "name": "Neon Sign",
            "attributes": []
        }
        
        r = self.client.post("/api/ai/generate-preview", json={
            "category_id": "66851234af504e44a4b8c771",
            "session_id": "test-session-uuid",
            "selected_attributes": {}
        })
        
        self.assertEqual(r.status_code, 429)
        self.assertFalse(r.json["success"])
        self.assertTrue(r.json["data"]["limit_reached"])
