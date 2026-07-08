import os
import sys
import unittest

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.utils.price_formula_helper import calculate_formula_price
from app.services.configurator_service import validate_attributes
from app.services.pricing_service import calculate_price
from app import create_app


class TestPriceFormulaHelper(unittest.TestCase):
    def test_calculate_formula_price_basic(self):
        extra_units, extra_cost = calculate_formula_price(16, 10, 25)
        self.assertEqual(extra_units, 6)
        self.assertEqual(extra_cost, 150)

    def test_calculate_formula_price_within_base(self):
        extra_units, extra_cost = calculate_formula_price(8, 10, 25)
        self.assertEqual(extra_units, 0)
        self.assertEqual(extra_cost, 0)

    def test_calculate_formula_price_invalid_inputs(self):
        self.assertEqual(calculate_formula_price("invalid", 10, 25), (0, 0))
        self.assertEqual(calculate_formula_price(None, 10, 25), (0, 0))
        self.assertEqual(calculate_formula_price(True, 10, 25), (0, 0))


class TestConfiguratorService(unittest.TestCase):
    def setUp(self):
        self.category = {
            "id": "cat_1",
            "attribute_schema": [
                {
                    "key": "font",
                    "label": "Font Style",
                    "type": "select",
                    "required": True,
                    "options": [
                        {"value": "cursive", "label": "Cursive", "price_delta": 150},
                        {"value": "bold", "label": "Bold", "price_delta": 100}
                    ]
                },
                {
                    "key": "chain",
                    "label": "Include Chain",
                    "type": "toggle",
                    "required": False,
                    "price_delta": 200
                },
                {
                    "key": "length",
                    "label": "Chain Length",
                    "type": "slider",
                    "min": 10,
                    "max": 30,
                    "price_formula": {
                        "base_included_units": 14,
                        "rate_per_unit": 30,
                        "unit": "inches"
                    }
                },
                {
                    "key": "engraving",
                    "label": "Engraving Text",
                    "type": "text_input",
                    "max_length": 15
                },
                {
                    "key": "legacy_option",
                    "label": "Legacy Option",
                    "type": "select",
                    "is_active": False,
                    "options": [{"value": "old", "label": "Old"}]
                }
            ]
        }

    def test_validate_valid_attributes(self):
        selected = {
            "font": "cursive",
            "chain": True,
            "length": 18,
            "engraving": "Hello World"
        }
        res = validate_attributes(self.category, selected)
        self.assertTrue(res["valid"])
        self.assertEqual(res["errors"], {})

    def test_validate_unknown_attribute(self):
        selected = {"font": "cursive", "hacker_key": "injection"}
        res = validate_attributes(self.category, selected)
        self.assertFalse(res["valid"])
        self.assertIn("hacker_key", res["errors"])

    def test_validate_missing_required(self):
        selected = {"chain": True}
        res = validate_attributes(self.category, selected)
        self.assertFalse(res["valid"])
        self.assertIn("font", res["errors"])

    def test_validate_invalid_option(self):
        selected = {"font": "italic"}
        res = validate_attributes(self.category, selected)
        self.assertFalse(res["valid"])
        self.assertIn("font", res["errors"])

    def test_validate_non_boolean_toggle(self):
        selected = {"font": "cursive", "chain": "yes"}
        res = validate_attributes(self.category, selected)
        self.assertFalse(res["valid"])
        self.assertIn("chain", res["errors"])

    def test_validate_slider_bounds(self):
        selected_low = {"font": "cursive", "length": 5}
        res_low = validate_attributes(self.category, selected_low)
        self.assertFalse(res_low["valid"])
        self.assertIn("length", res_low["errors"])

        selected_high = {"font": "cursive", "length": 35}
        res_high = validate_attributes(self.category, selected_high)
        self.assertFalse(res_high["valid"])
        self.assertIn("length", res_high["errors"])

    def test_validate_text_max_length(self):
        selected = {"font": "cursive", "engraving": "This string is way too long for fifteen characters"}
        res = validate_attributes(self.category, selected)
        self.assertFalse(res["valid"])
        self.assertIn("engraving", res["errors"])

    def test_validate_disabled_attribute(self):
        selected = {"font": "cursive", "legacy_option": "old"}
        res = validate_attributes(self.category, selected)
        self.assertFalse(res["valid"])
        self.assertIn("legacy_option", res["errors"])


class TestPricingService(unittest.TestCase):
    def setUp(self):
        self.product = {
            "id": "prod_1",
            "base_price": 1499
        }
        self.category = {
            "id": "cat_1",
            "attribute_schema": [
                {
                    "key": "font",
                    "label": "Font Style",
                    "type": "select",
                    "options": [
                        {"value": "cursive", "label": "Cursive", "price_delta": 150},
                        {"value": "bold", "label": "Bold", "price_delta": 100}
                    ]
                },
                {
                    "key": "chain",
                    "label": "Include Chain",
                    "type": "toggle",
                    "price_delta": 200
                },
                {
                    "key": "length",
                    "label": "Chain Length",
                    "type": "slider",
                    "price_formula": {
                        "base_included_units": 14,
                        "rate_per_unit": 30,
                        "unit": "inches"
                    }
                },
                {
                    "key": "engraving",
                    "label": "Engraving Text",
                    "type": "text_input"
                }
            ]
        }

    def test_calculate_price_comprehensive(self):
        selected = {
            "font": "cursive",   # +150
            "chain": True,       # +200
            "length": 18,        # + (18-14)*30 = +120
            "engraving": "LIT"   # +0
        }
        res = calculate_price(self.product, self.category, selected, quantity=2)
        
        # Unit price = 1499 + 150 + 200 + 120 = 1969
        self.assertEqual(res["unit_price"], 1969)
        self.assertEqual(res["quantity"], 2)
        self.assertEqual(res["line_total"], 1969 * 2)

        breakdown_keys = [item["key"] for item in res["breakdown"]]
        self.assertEqual(breakdown_keys, ["base_price", "font", "chain", "length"])


class TestConfiguratorRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.category = {
            "id": "cat_1",
            "attribute_schema": [
                {
                    "key": "font",
                    "label": "Font Style",
                    "type": "select",
                    "required": True,
                    "options": [
                        {"value": "cursive", "label": "Cursive", "price_delta": 150}
                    ]
                }
            ]
        }
        self.product = {
            "id": "prod_1",
            "base_price": 1000
        }

    def test_validate_route(self):
        payload = {
            "category": self.category,
            "selected_attributes": {"font": "cursive"}
        }
        resp = self.client.post("/api/configurator/validate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["data"]["valid"])

    def test_price_route_valid(self):
        payload = {
            "product": self.product,
            "category": self.category,
            "selected_attributes": {"font": "cursive"},
            "quantity": 3
        }
        resp = self.client.post("/api/configurator/price", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["unit_price"], 1150)
        self.assertEqual(data["data"]["line_total"], 3450)

    def test_price_route_invalid_attributes(self):
        payload = {
            "product": self.product,
            "category": self.category,
            "selected_attributes": {"font": "invalid"}
        }
        resp = self.client.post("/api/configurator/price", json=payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertFalse(data["success"])
        self.assertFalse(data["data"]["valid"])


if __name__ == "__main__":
    unittest.main()
