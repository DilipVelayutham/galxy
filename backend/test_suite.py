import json
import unittest
import unittest.mock
import uuid
import datetime
from bson import ObjectId

# Set environment variables for testing before imports
import os
os.environ["MOCK_AI"] = "True"
os.environ["AI_FREE_GENERATIONS_PER_SESSION"] = "5"
os.environ["AI_MAX_GENERATIONS_PER_USER_PER_DAY"] = "20"

from app import create_app
from app.database import categories, ai_generations, ai_cache

class TestAIPreviewGeneration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        
        cls.category_id = "test_custom_apparels"
        
        # Always create/overwrite a clean test category schema for unit tests
        categories.update_one(
            {"category_id": cls.category_id},
            {"$set": {
                "category_id": cls.category_id,
                "slug": "test-custom-apparels",
                "name": "Test Custom Apparels",
                "is_active": True,
                "ai_prompt_template": "A {color} {style} with '{custom_text}' logo.",
                "attribute_schema": [
                    {"key": "style", "label": "Style", "type": "select", "required": True, "affects_ai_preview": True, "options": [{"value": "tshirt", "label": "T-Shirt"}]},
                    {"key": "color", "label": "Color", "type": "color_swatch", "required": True, "affects_ai_preview": True, "options": [{"value": "black", "label": "Black"}]},
                    {"key": "custom_text", "label": "Text", "type": "text_input", "required": True, "affects_ai_preview": True}
                ]
            }},
            upsert=True
        )
        cls.category_doc = categories.find_one({"category_id": cls.category_id})
        
    @classmethod
    def tearDownClass(cls):
        # Clean up test category
        categories.delete_one({"category_id": cls.category_id})
            
    def setUp(self):
        # Clear database collection logs for clean test runs
        ai_generations.delete_many({})
        ai_cache.delete_many({})

    def test_01_successful_generation(self):
        """Test standard preview generation route."""
        payload = {
            "category_id": self.category_id,
            "selected_attributes": {
                "style": "tshirt",
                "color": "black",
                "custom_text": "LTI Hub"
            },
            "session_id": str(uuid.uuid4())
        }
        
        response = self.client.post('/api/ai/generate-preview', 
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("output_image_url", data["data"])
        self.assertFalse(data["data"]["from_cache"])
        self.assertIn("generation_id", data["data"])
        
        # Verify db logging occurred
        generation_doc = ai_generations.find_one({"_id": ObjectId(data["data"]["generation_id"])})
        self.assertIsNotNone(generation_doc)
        self.assertEqual(generation_doc["status"], "success")
        self.assertTrue(generation_doc["generation_time_ms"] > 0)
        
    def test_02_validation_error(self):
        """Test validation failures."""
        # 1. Invalid option value
        payload_invalid_option = {
            "category_id": self.category_id,
            "selected_attributes": {
                "style": "jeans", # Invalid option
                "color": "black",
                "custom_text": "LTI Hub"
            }
        }
        response = self.client.post('/api/ai/generate-preview', 
                                   data=json.dumps(payload_invalid_option),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertFalse(data["success"])
        self.assertIn("errors", data)

    def test_03_caching_and_bypass(self):
        """Test cache hit triggers and custom_text cache bypass checks."""
        # Note: to test caching, we need a payload without custom_text.
        # Let's create a temporary category that doesn't require custom_text
        temp_cat_id = "cache_test_category"
        categories.update_one(
            {"category_id": temp_cat_id},
            {"$set": {
                "category_id": temp_cat_id,
                "name": "Cache Test Category",
                "ai_prompt_template": "A {color} {style}.",
                "attribute_schema": [
                    {"key": "style", "label": "Style", "type": "select", "required": True, "affects_ai_preview": True, "options": [{"value": "tshirt", "label": "T-Shirt"}]},
                    {"key": "color", "label": "Color", "type": "color_swatch", "required": True, "affects_ai_preview": True, "options": [{"value": "black", "label": "Black"}]}
                ]
            }},
            upsert=True
        )
        
        payload = {
            "category_id": temp_cat_id,
            "selected_attributes": {
                "style": "tshirt",
                "color": "black"
            },
            "session_id": str(uuid.uuid4())
        }
        
        # First query: Cache Miss
        response1 = self.client.post('/api/ai/generate-preview', 
                                    data=json.dumps(payload),
                                    content_type='application/json')
        data1 = json.loads(response1.data.decode('utf-8'))
        self.assertFalse(data1["data"]["from_cache"])
        
        # Second query: Cache Hit
        response2 = self.client.post('/api/ai/generate-preview', 
                                    data=json.dumps(payload),
                                    content_type='application/json')
        data2 = json.loads(response2.data.decode('utf-8'))
        self.assertTrue(data2["data"]["from_cache"])
        
        # Verify cache hit logged with generation_time_ms: 0
        hit_doc = ai_generations.find_one({"_id": ObjectId(data2["data"]["generation_id"])})
        self.assertEqual(hit_doc["generation_time_ms"], 0)
        
        # Cleanup
        categories.delete_one({"category_id": temp_cat_id})

    def test_04_rate_limiting(self):
        """Test guest user session rate limit block at 5 successful calls."""
        session_id = f"test_session_{uuid.uuid4()}"
        payload = {
            "category_id": self.category_id,
            "selected_attributes": {
                "style": "tshirt",
                "color": "black",
                "custom_text": "LTI"
            },
            "session_id": session_id
        }
        
        # First 5 calls must be allowed
        for i in range(5):
            # Change text slightly to bypass caching (which would exempt it from rate counts)
            payload["selected_attributes"]["custom_text"] = f"LTI {i}"
            response = self.client.post('/api/ai/generate-preview', 
                                       data=json.dumps(payload),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 200)
            
        # 6th call must be blocked with HTTP 429
        payload["selected_attributes"]["custom_text"] = "LTI Block"
        response = self.client.post('/api/ai/generate-preview', 
                                   data=json.dumps(payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 429)

    def test_05_auth_and_history(self):
        """Test security gates and history endpoints."""
        user_id = "user_12345"
        payload = {
            "category_id": self.category_id,
            "selected_attributes": {
                "style": "tshirt",
                "color": "black",
                "custom_text": "History Test"
            },
            "user_id": user_id
        }
        
        # Generate items
        self.client.post('/api/ai/generate-preview', data=json.dumps(payload), content_type='application/json')
        
        # 1. Test history endpoint without X-User-Id (should return 401)
        resp = self.client.get(f'/api/ai/generations/{user_id}')
        self.assertEqual(resp.status_code, 401)
        
        # 2. Test history endpoint with mismatched X-User-Id (should return 403)
        headers = {"X-User-Id": "other_user_id"}
        resp = self.client.get(f'/api/ai/generations/{user_id}', headers=headers)
        self.assertEqual(resp.status_code, 403)
        
        # 3. Test history endpoint with valid X-User-Id (should return 200)
        headers = {"X-User-Id": user_id}
        resp = self.client.get(f'/api/ai/generations/{user_id}', headers=headers)
        self.assertEqual(resp.status_code, 200)
        
    def test_06_admin_analytics_cursor(self):
        """Test admin analytics cursor-based pagination."""
        # Generate 3 items
        payload = {
            "category_id": self.category_id,
            "selected_attributes": {"style": "tshirt", "color": "black", "custom_text": "A"},
            "session_id": "session_A"
        }
        for i in range(3):
            payload["selected_attributes"]["custom_text"] = f"A {i}"
            self.client.post('/api/ai/generate-preview', data=json.dumps(payload), content_type='application/json')
            
        # 1. Admin GET without role header (should return 403)
        resp = self.client.get('/api/admin/ai/generations')
        self.assertEqual(resp.status_code, 403)
        
        # 2. Admin GET with admin header (should return 200 and cursor info)
        headers = {"X-User-Role": "admin"}
        resp = self.client.get('/api/admin/ai/generations?limit=2', headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data.decode('utf-8'))
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]), 2)
        self.assertIn("next_cursor", data)
        self.assertTrue(data["has_more"])
        
        # 3. Request page 2 with next_cursor
        cursor_id = data["next_cursor"]
        resp_p2 = self.client.get(f'/api/admin/ai/generations?limit=2&next_cursor={cursor_id}', headers=headers)
        self.assertEqual(resp_p2.status_code, 200)
        data_p2 = json.loads(resp_p2.data.decode('utf-8'))
        self.assertEqual(len(data_p2["data"]), 1)
        self.assertFalse(data_p2["has_more"])

    def test_07_rate_limiting_by_ip(self):
        """Test guest user rate limit block by IP address when session_id changes (incognito bypass attempt)."""
        ip_addr = "192.168.1.99"
        payload = {
            "category_id": self.category_id,
            "selected_attributes": {
                "style": "tshirt",
                "color": "black",
                "custom_text": "LTI"
            }
        }
        
        # 5 calls from the same IP, but with different session_ids, should be allowed
        for i in range(5):
            payload["session_id"] = f"session_{i}_{uuid.uuid4()}"
            payload["selected_attributes"]["custom_text"] = f"LTI {i}"
            response = self.client.post('/api/ai/generate-preview', 
                                       environ_base={'REMOTE_ADDR': ip_addr},
                                       data=json.dumps(payload),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 200)
            
        # 6th call from the same IP with a new session_id must be blocked by IP rate limit
        payload["session_id"] = f"session_bypass_{uuid.uuid4()}"
        payload["selected_attributes"]["custom_text"] = "LTI Blocked IP"
        response = self.client.post('/api/ai/generate-preview', 
                                   environ_base={'REMOTE_ADDR': ip_addr},
                                   data=json.dumps(payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 429)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data["data"]["limit_scope"], "ip")

    @unittest.mock.patch('cloudinary.uploader.upload')
    @unittest.mock.patch('cloudinary.uploader.destroy')
    @unittest.mock.patch('app.database.ai_generations.insert_one')
    def test_08_cloudinary_orphan_rollback(self, mock_insert_one, mock_destroy, mock_upload):
        """Test that Cloudinary upload is rolled back if database insertion fails."""
        # Mock successful Cloudinary upload
        mock_upload.return_value = {
            "secure_url": "https://res.cloudinary.com/test/image/upload/v1/test.png",
            "public_id": "galxy/ai-previews/test_public_id"
        }
        
        # Mock database insertion error
        mock_insert_one.side_effect = Exception("Simulated database failure")
        
        payload = {
            "category_id": self.category_id,
            "selected_attributes": {
                "style": "tshirt",
                "color": "black",
                "custom_text": "Rollback Test"
            },
            "session_id": "session_rollback_test"
        }
        
        response = self.client.post('/api/ai/generate-preview', 
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        # Should return 502 error
        self.assertEqual(response.status_code, 502)
        
        # Verify Cloudinary destroy was called for the uploaded image public_id
        mock_destroy.assert_called_once_with("galxy/ai-previews/test_public_id")

if __name__ == '__main__':
    unittest.main()
