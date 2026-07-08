import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from bson import ObjectId
from datetime import datetime

# Resolve project path to find 'app' package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.services import testimonial_service


class TestTestimonialsModule(unittest.TestCase):
    def setUp(self):
        """Set up Flask test client and config mock environment."""
        from app.database.db import db
        db.init_app = MagicMock()
        db.db = MagicMock()

        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["FLASK_ENV"] = "development"
        self.app.config["JWT_SECRET"] = "test_jwt_secret"
        self.client = self.app.test_client()

        # Headers for authenticated admin
        self.admin_headers = {
            "Authorization": "Bearer mock-admin-token"
        }

    def test_health_check(self):
        """Test health check route."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("running", data["message"])

    @patch("app.database.db.Database.get_collection")
    def test_list_testimonials_public(self, mock_get_collection):
        """Test public endpoint fetching active testimonials with projection."""
        mock_coll = MagicMock()
        mock_get_collection.return_value = mock_coll

        # Mock find return value
        mock_coll.find.return_value.sort.return_value = [
            {
                "customer_name": "Aravind",
                "customer_location": "Chennai",
                "quote": "Amazing neon board!",
                "rating": 5,
                "image": "cloudinary://neon1"
            },
            {
                "customer_name": "Deepa",
                "customer_location": "Bangalore",
                "quote": "Beautiful quilling art.",
                "rating": 4,
                "image": None
            }
        ]

        response = self.client.get("/api/testimonials")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]), 2)
        
        # Verify public projection (no _id, no is_active, no review_id, no source)
        for doc in data["data"]:
            self.assertNotIn("id", doc)
            self.assertNotIn("_id", doc)
            self.assertNotIn("is_active", doc)
            self.assertNotIn("review_id", doc)
            self.assertNotIn("source", doc)
            self.assertIn("customer_name", doc)
            self.assertIn("customer_location", doc)
            self.assertIn("quote", doc)
            self.assertIn("rating", doc)
            self.assertIn("image", doc)

        self.assertEqual(data["data"][0]["customer_name"], "Aravind")
        self.assertEqual(data["data"][1]["customer_name"], "Deepa")

        # Verify find was called with active filter
        mock_coll.find.assert_called_once_with({"is_active": True}, {
            "_id": 0, "customer_name": 1, "customer_location": 1,
            "quote": 1, "rating": 1, "image": 1
        })

    def test_admin_route_unauthorized(self):
        """Test admin routes without authorization fail with 401."""
        endpoints = [
            ("/api/admin/testimonials", "GET", None),
            ("/api/admin/testimonials", "POST", {}),
            ("/api/admin/testimonials/603f9a7f3f2d2b0015b6d92f", "PUT", {}),
            ("/api/admin/testimonials/603f9a7f3f2d2b0015b6d92f", "DELETE", None),
            ("/api/admin/testimonials/reorder", "PUT", {"order": []})
        ]
        
        for url, method, json_data in endpoints:
            if method == "GET":
                res = self.client.get(url)
            elif method == "POST":
                res = self.client.post(url, json=json_data)
            elif method == "PUT":
                res = self.client.put(url, json=json_data)
            elif method == "DELETE":
                res = self.client.delete(url)
            
            self.assertEqual(res.status_code, 401, f"URL {url} failed with {res.status_code}")
            data = res.get_json()
            self.assertFalse(data["success"])
            self.assertIn("Token is missing", data["message"])

    @patch("app.database.db.Database.get_collection")
    def test_admin_list_testimonials(self, mock_get_collection):
        """Test admin list testimonials retrieves all entries with all fields."""
        mock_coll = MagicMock()
        mock_get_collection.return_value = mock_coll

        mock_coll.find.return_value.sort.return_value = [
            {
                "_id": ObjectId("603f9a7f3f2d2b0015b6d92f"),
                "customer_name": "Aravind",
                "customer_location": "Chennai",
                "quote": "Amazing neon board!",
                "rating": 5,
                "image": "cloudinary://neon1",
                "is_active": True,
                "source": "manual",
                "review_id": None,
                "created_at": datetime.utcnow()
            }
        ]

        response = self.client.get("/api/admin/testimonials", headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["id"], "603f9a7f3f2d2b0015b6d92f")
        self.assertEqual(data["data"][0]["source"], "manual")
        self.assertTrue(data["data"][0]["is_active"])

    @patch("app.database.db.Database.get_collection")
    def test_admin_get_testimonial_detail(self, mock_get_collection):
        """Test admin fetch single testimonial detail by ID."""
        mock_coll = MagicMock()
        mock_get_collection.return_value = mock_coll

        oid = ObjectId("603f9a7f3f2d2b0015b6d92f")
        mock_coll.find_one.return_value = {
            "_id": oid,
            "customer_name": "Aravind",
            "customer_location": "Chennai",
            "quote": "Amazing neon board!",
            "rating": 5,
            "image": "cloudinary://neon1",
            "is_active": True,
            "source": "manual",
            "review_id": None,
            "created_at": datetime.utcnow()
        }

        response = self.client.get(f"/api/admin/testimonials/{str(oid)}", headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["id"], str(oid))
        self.assertEqual(data["data"]["customer_name"], "Aravind")

    @patch("app.database.db.Database.get_collection")
    def test_admin_create_testimonial_success(self, mock_get_collection):
        """Test admin successfully creates a manual testimonial."""
        mock_coll = MagicMock()
        mock_get_collection.return_value = mock_coll

        oid = ObjectId("603f9a7f3f2d2b0015b6d92f")
        mock_coll.insert_one.return_value.inserted_id = oid

        payload = {
            "customer_name": "Pooja",
            "customer_location": "Coimbatore",
            "quote": "Beautiful custom lamp!",
            "rating": 4,
            "image": "cloudinary://lamp1",
            "display_order": 2,
            "is_active": True
        }

        response = self.client.post("/api/admin/testimonials", json=payload, headers=self.admin_headers)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["id"], str(oid))
        self.assertEqual(data["data"]["customer_name"], "Pooja")
        self.assertEqual(data["data"]["source"], "manual")  # Overriden by route to manual
        self.assertEqual(data["data"]["review_id"], None)

    @patch("app.database.db.Database.get_collection")
    def test_admin_create_testimonial_validation_failure(self, mock_get_collection):
        """Test creation fails with invalid rating or missing fields."""
        payload = {
            "customer_name": "Pooja",
            # Missing quote
            "rating": 6  # Invalid rating
        }

        response = self.client.post("/api/admin/testimonials", json=payload, headers=self.admin_headers)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("quote is required", data["message"])
        self.assertIn("rating must be between 1 and 5", data["message"])

    @patch("app.database.db.Database.get_collection")
    def test_admin_update_testimonial_success(self, mock_get_collection):
        """Test admin updates testimonial fields successfully."""
        mock_coll = MagicMock()
        mock_get_collection.return_value = mock_coll

        oid = ObjectId("603f9a7f3f2d2b0015b6d92f")
        mock_coll.update_one.return_value.matched_count = 1
        mock_coll.find_one.return_value = {
            "_id": oid,
            "customer_name": "Aravind Updated",
            "customer_location": "Chennai",
            "quote": "Amazing neon board!",
            "rating": 5,
            "image": "cloudinary://neon1",
            "is_active": False,
            "source": "manual",
            "review_id": None
        }

        payload = {
            "customer_name": "Aravind Updated",
            "is_active": False
        }

        response = self.client.put(f"/api/admin/testimonials/{str(oid)}", json=payload, headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["customer_name"], "Aravind Updated")
        self.assertFalse(data["data"]["is_active"])

    @patch("app.database.db.Database.get_collection")
    def test_admin_delete_testimonial(self, mock_get_collection):
        """Test admin hard deletes testimonial."""
        mock_coll = MagicMock()
        mock_get_collection.return_value = mock_coll

        oid = ObjectId("603f9a7f3f2d2b0015b6d92f")
        mock_coll.delete_one.return_value.deleted_count = 1

        response = self.client.delete(f"/api/admin/testimonials/{str(oid)}", headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Testimonial deleted successfully")
        mock_coll.delete_one.assert_called_once_with({"_id": oid})

    @patch("app.database.db.Database.get_collection")
    def test_admin_reorder_testimonials(self, mock_get_collection):
        """Test admin bulk reorders testimonials."""
        mock_coll = MagicMock()
        mock_get_collection.return_value = mock_coll

        payload = {
            "order": [
                {"testimonial_id": "603f9a7f3f2d2b0015b6d92f", "display_order": 5},
                {"testimonial_id": "603f9a7f3f2d2b0015b6d930", "display_order": 10}
            ]
        }

        response = self.client.put("/api/admin/testimonials/reorder", json=payload, headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Testimonials reordered successfully")
        self.assertEqual(mock_coll.bulk_write.call_count, 1)

    @patch("app.database.db.Database.get_collection")
    def test_promote_review_service_helper(self, mock_get_collection):
        """Test promoting review copies correct data into testimonial doc."""
        mock_coll = MagicMock()
        mock_get_collection.return_value = mock_coll

        review_oid = ObjectId("503f9a7f3f2d2b0015b6d92a")
        testimonial_oid = ObjectId("603f9a7f3f2d2b0015b6d92f")
        mock_coll.insert_one.return_value.inserted_id = testimonial_oid

        review_data = {
            "customer_name": "Suresh",
            "comment": "Outstanding craftsmanship!",
            "rating": 5,
            "images": ["cloudinary://craft_image"]
        }

        result = testimonial_service.promote_review_to_testimonial(
            review_id=str(review_oid),
            review_data=review_data,
            customer_location="Madurai",
            display_order=15
        )

        self.assertEqual(result["customer_name"], "Suresh")
        self.assertEqual(result["customer_location"], "Madurai")
        self.assertEqual(result["quote"], "Outstanding craftsmanship!")
        self.assertEqual(result["rating"], 5)
        self.assertEqual(result["image"], "cloudinary://craft_image")
        self.assertEqual(result["display_order"], 15)
        self.assertEqual(result["source"], "review")
        self.assertEqual(result["review_id"], str(review_oid))


if __name__ == "__main__":
    unittest.main()
