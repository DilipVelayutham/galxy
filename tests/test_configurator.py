import unittest
from unittest.mock import MagicMock, patch
from bson import ObjectId

from services.configurator_service import validate_attributes, calculate_price

class TestConfigurator(unittest.TestCase):
    
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_categories = MagicMock()
        self.mock_products = MagicMock()
        self.mock_db.categories = self.mock_categories
        self.mock_db.products = self.mock_products
        
        # Patch db connection in configurator_service
        self.patcher = patch("services.configurator_service.db", self.mock_db)
        self.patcher.start()
        
        # Mock Category Data with Attribute Schemas
        self.category_id = ObjectId()
        self.category_data = {
            "_id": self.category_id,
            "name": "Neon Name Boards",
            "slug": "neon-name-boards",
            "attribute_schema": [
                {
                    "key": "font",
                    "label": "Font Style",
                    "type": "select",
                    "required": True,
                    "options": [
                        {"value": "cursive", "label": "Cursive", "price_delta": 0.0},
                        {"value": "bold", "label": "Bold", "price_delta": 25.0}
                    ]
                },
                {
                    "key": "backing",
                    "label": "Backing Acrylic Cut",
                    "type": "select",
                    "required": False,
                    "options": [
                        {"value": "cut_to_shape", "label": "Cut to Shape", "price_delta": 10.0},
                        {"value": "whole_board", "label": "Whole Board", "price_delta": 30.0}
                    ]
                },
                {
                    "key": "with_dimmer",
                    "label": "Include Dimmer",
                    "type": "toggle",
                    "required": False
                },
                {
                    "key": "size_inches",
                    "label": "Width in Inches",
                    "type": "slider",
                    "required": True,
                    "min": 12.0,
                    "max": 48.0,
                    "step": 2.0
                }
            ]
        }
        
        # Mock Product Data
        self.product_id = ObjectId()
        self.product_data = {
            "_id": self.product_id,
            "category_id": self.category_id,
            "title": "Custom Neon Board",
            "slug": "custom-neon-board",
            "base_price": 150.0
        }

    def tearDown(self):
        self.patcher.stop()

    def test_validate_attributes_success(self):
        self.mock_categories.find_one.return_value = self.category_data
        
        valid_attributes = {
            "font": "cursive",
            "backing": "whole_board",
            "with_dimmer": True,
            "size_inches": 24.0
        }
        
        result = validate_attributes(self.category_id, valid_attributes)
        self.assertTrue(result)

    def test_validate_attributes_missing_required(self):
        self.mock_categories.find_one.return_value = self.category_data
        
        # Missing 'font' (required)
        invalid_attributes = {
            "size_inches": 24.0
        }
        
        with self.assertRaises(ValueError) as context:
            validate_attributes(self.category_id, invalid_attributes)
        self.assertIn("required", str(context.exception))

    def test_validate_attributes_invalid_select_option(self):
        self.mock_categories.find_one.return_value = self.category_data
        
        # 'font' value 'italic' is not in options
        invalid_attributes = {
            "font": "italic",
            "size_inches": 24.0
        }
        
        with self.assertRaises(ValueError) as context:
            validate_attributes(self.category_id, invalid_attributes)
        self.assertIn("Invalid option", str(context.exception))

    def test_validate_attributes_invalid_toggle_type(self):
        self.mock_categories.find_one.return_value = self.category_data
        
        # 'with_dimmer' toggle must be boolean
        invalid_attributes = {
            "font": "cursive",
            "with_dimmer": "Yes please",
            "size_inches": 24.0
        }
        
        with self.assertRaises(ValueError) as context:
            validate_attributes(self.category_id, invalid_attributes)
        self.assertIn("must be a boolean", str(context.exception))

    def test_validate_attributes_slider_boundaries(self):
        self.mock_categories.find_one.return_value = self.category_data
        
        # size_inches = 10 is below min = 12
        invalid_attributes = {
            "font": "cursive",
            "size_inches": 10.0
        }
        with self.assertRaises(ValueError) as context:
            validate_attributes(self.category_id, invalid_attributes)
        self.assertIn("below minimum", str(context.exception))
        
        # size_inches = 50 is above max = 48
        invalid_attributes = {
            "font": "cursive",
            "size_inches": 50.0
        }
        with self.assertRaises(ValueError) as context:
            validate_attributes(self.category_id, invalid_attributes)
        self.assertIn("above maximum", str(context.exception))

    def test_validate_attributes_unrecognized_key(self):
        self.mock_categories.find_one.return_value = self.category_data
        
        # 'extra_key' is not in category attribute_schema
        invalid_attributes = {
            "font": "cursive",
            "size_inches": 24.0,
            "extra_key": "some_value"
        }
        
        with self.assertRaises(ValueError) as context:
            validate_attributes(self.category_id, invalid_attributes)
        self.assertIn("Unrecognized attributes", str(context.exception))

    def test_calculate_price_success(self):
        self.mock_products.find_one.return_value = self.product_data
        self.mock_categories.find_one.return_value = self.category_data
        
        # Select options with known surcharges:
        # font 'bold' (+25.0)
        # backing 'whole_board' (+30.0)
        # base_price: 150.0
        selected_attributes = {
            "font": "bold",
            "backing": "whole_board",
            "with_dimmer": True,
            "size_inches": 24.0
        }
        
        price_info = calculate_price(self.product_id, selected_attributes)
        
        self.assertEqual(price_info["base_price"], 150.0)
        self.assertEqual(price_info["surcharges"], 55.0) # 25 + 30
        self.assertEqual(price_info["unit_price"], 205.0) # 150 + 55

if __name__ == "__main__":
    unittest.main()
