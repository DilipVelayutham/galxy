import os
os.environ["TESTING"] = "True"

import unittest
from unittest.mock import MagicMock, patch
from bson import ObjectId
import importlib.util
spec = importlib.util.spec_from_file_location("app_root", os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py")))
app_root = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_root)
app = app_root.app
from models.cart import create_empty_cart

class TestAPIEndpoints(unittest.TestCase):
    
    def setUp(self):
        # Create client for testing
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Set up database mocks
        self.mock_db = MagicMock()
        self.mock_carts = MagicMock()
        self.mock_products = MagicMock()
        self.mock_categories = MagicMock()
        
        self.mock_db.carts = self.mock_carts
        self.mock_db.products = self.mock_products
        self.mock_db.categories = self.mock_categories
        
        # Patch the database instances in routes/services
        self.patchers = [
            patch("services.cart_service.db", self.mock_db),
            patch("services.configurator_service.db", self.mock_db),
            patch("services.product_service.db", self.mock_db)
        ]
        
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()
        self.app_context.pop()

    def test_get_cart_endpoint_success(self):
        # Setup mock db find_one
        cart_data = create_empty_cart("test_user_id")
        cart_data["_id"] = ObjectId()
        self.mock_carts.find_one.return_value = cart_data
        
        response = self.client.get("/api/cart", headers={"X-User-Id": "test_user_id"})
        self.assertEqual(response.status_code, 200)
        
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["message"], "Cart retrieved successfully.")
        self.assertEqual(json_data["data"]["user_id"], "test_user_id")

    def test_add_item_endpoint_success(self):
        # Setup mock product, category, and cart
        product_id = ObjectId()
        category_id = ObjectId()
        
        product_data = {
            "_id": product_id,
            "category_id": category_id,
            "title": "Custom Name Board",
            "base_price": 100.0,
            "thumbnail": "watch.jpg",
            "description": "Custom Watch"
        }
        
        category_data = {
            "_id": category_id,
            "name": "Neon Boards",
            "attribute_schema": [
                {
                    "key": "color",
                    "label": "Color",
                    "type": "select",
                    "required": True,
                    "options": [{"value": "Pink", "label": "Pink", "price_delta": 10.0}]
                }
            ]
        }
        
        cart_data = create_empty_cart("test_user_id")
        cart_data["_id"] = ObjectId()
        
        self.mock_products.find_one.return_value = product_data
        self.mock_categories.find_one.return_value = category_data
        self.mock_carts.find_one.return_value = cart_data
        
        payload = {
            "product_id": str(product_id),
            "selected_attributes": {"color": "Pink"},
            "custom_text": "Neon Glow",
            "quantity": 2
        }
        
        response = self.client.post(
            "/api/cart/items",
            json=payload,
            headers={"X-User-Id": "test_user_id"}
        )
        self.assertEqual(response.status_code, 200)
        
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["message"], "Item added to cart.")
        
        # Verify totals: base (100) + color delta (10) = 110. qty = 2 -> subtotal = 220
        self.assertEqual(json_data["data"]["price_breakdown"]["subtotal"], 220.0)

    def test_configurator_validate_endpoint_success(self):
        category_id = ObjectId()
        category_data = {
            "_id": category_id,
            "name": "Neon Boards",
            "attribute_schema": []
        }
        self.mock_categories.find_one.return_value = category_data
        
        payload = {
            "category_id": str(category_id),
            "selected_attributes": {}
        }
        
        response = self.client.post("/api/configurator/validate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertTrue(json_data["data"]["valid"])

    def test_configurator_validate_endpoint_missing_category(self):
        payload = {
            "selected_attributes": {}
        }
        # missing category_id
        response = self.client.post("/api/configurator/validate", json=payload)
        self.assertEqual(response.status_code, 400)
        
        json_data = response.get_json()
        self.assertFalse(json_data["success"])
        self.assertIn("category_id is required", json_data["errors"]["category_id"])

    def test_configurator_price_endpoint_success(self):
        product_id = ObjectId()
        product_data = {
            "_id": product_id,
            "category_id": None,
            "title": "Neon Simple Board",
            "base_price": 50.0
        }
        self.mock_products.find_one.return_value = product_data
        
        payload = {
            "product_id": str(product_id),
            "selected_attributes": {}
        }
        
        response = self.client.post("/api/configurator/price", json=payload)
        self.assertEqual(response.status_code, 200)
        
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["data"]["unit_price"], 50.0)

if __name__ == "__main__":
    unittest.main()
