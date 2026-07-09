import unittest
from unittest.mock import MagicMock, patch

# Import models & service functions to test
from models.cart import (
    create_empty_cart,
    construct_cart_item,
    are_items_duplicate,
    recalculate_cart_totals
)

# We will patch the db object from services.cart_service or db.py
# inside the tests so that PyMongo does not attempt real network calls.

class TestCartModels(unittest.TestCase):
    
    def test_create_empty_cart(self):
        cart = create_empty_cart("user_123")
        self.assertEqual(cart["user_id"], "user_123")
        self.assertEqual(len(cart["items"]), 0)
        self.assertEqual(cart["price_breakdown"]["subtotal"], 0.0)
        self.assertEqual(cart["price_breakdown"]["total"], 0.0)
        self.assertIsNotNone(cart["created_at"])
        
    def test_construct_cart_item_valid(self):
        snapshot = {"name": "Shirt", "category": "Apparel"}
        item = construct_cart_item(
            product_id="prod_01",
            quantity=2,
            selected_attributes={"size": "M"},
            custom_text="Hello",
            unit_price=19.99,
            snapshot=snapshot
        )
        self.assertIsNotNone(item["item_id"])
        self.assertEqual(item["product_id"], "prod_01")
        self.assertEqual(item["quantity"], 2)
        self.assertEqual(item["selected_attributes"], {"size": "M"})
        self.assertEqual(item["custom_text"], "Hello")
        self.assertEqual(item["unit_price"], 19.99)
        self.assertEqual(item["line_total"], 39.98)
        self.assertEqual(item["snapshot"], snapshot)

    def test_construct_cart_item_invalid_quantity(self):
        with self.assertRaises(ValueError):
            construct_cart_item("prod_01", 0, {}, "", 10.0, {})
            
        with self.assertRaises(ValueError):
            construct_cart_item("prod_01", -5, {}, "", 10.0, {})

    def test_are_items_duplicate(self):
        item1 = {
            "product_id": "prod_01",
            "selected_attributes": {"color": "Blue"},
            "custom_text": "Greetings "
        }
        item2 = {
            "product_id": "prod_01",
            "selected_attributes": {"color": "Blue"},
            "custom_text": "Greetings"
        }
        item3 = {
            "product_id": "prod_01",
            "selected_attributes": {"color": "Red"},
            "custom_text": "Greetings"
        }
        item4 = {
            "product_id": "prod_02",
            "selected_attributes": {"color": "Blue"},
            "custom_text": "Greetings"
        }
        
        # item1 and item2 are duplicates (strip on custom_text makes them equal)
        self.assertTrue(are_items_duplicate(item1, item2))
        # item1 and item3 differ in attributes
        self.assertFalse(are_items_duplicate(item1, item3))
        # item1 and item4 differ in product_id
        self.assertFalse(are_items_duplicate(item1, item4))

    def test_recalculate_cart_totals(self):
        cart = create_empty_cart("user_1")
        cart["items"] = [
            {"line_total": 20.0},
            {"line_total": 45.50}
        ]
        cart["price_breakdown"]["shipping"] = 5.0
        cart["price_breakdown"]["tax"] = 2.0
        cart["price_breakdown"]["discount"] = 10.0
        
        recalculate_cart_totals(cart)
        # subtotal: 20 + 45.5 = 65.5
        # total: 65.5 + 5 (shipping) + 2 (tax) - 10 (discount) = 62.5
        self.assertEqual(cart["price_breakdown"]["subtotal"], 65.50)
        self.assertEqual(cart["price_breakdown"]["total"], 62.50)


class TestCartService(unittest.TestCase):
    
    def setUp(self):
        # Setup mock db and collections
        self.mock_db = MagicMock()
        self.mock_carts_col = MagicMock()
        self.mock_db.carts = self.mock_carts_col
        
        # Patch the imported db client in cart_service
        self.patcher = patch("services.cart_service.db", self.mock_db)
        self.patcher.start()
        
        # Mock external configurator & product service dependencies to keep unit tests isolated
        self.patch_validate = patch("services.cart_service.validate_attributes", return_value=True)
        self.patch_validate.start()
        
        # Mock calculate_price to return a realistic price matching previous mock logic
        def mock_calc_price(product_id, selected_attributes):
            base_price = 100.0
            surcharge = 0.0
            if product_id == "premium_product":
                base_price = 500.0
                if selected_attributes and selected_attributes.get("color") == "Gold":
                    surcharge = 50.0
                elif selected_attributes and selected_attributes.get("color") == "Silver":
                    surcharge = 5.0
            elif product_id == "budget_product":
                base_price = 20.0
                if selected_attributes and selected_attributes.get("size") == "M":
                    surcharge = 5.0
            return {
                "base_price": base_price,
                "surcharges": surcharge,
                "unit_price": base_price + surcharge
            }
        self.patch_price = patch("services.cart_service.calculate_price", side_effect=mock_calc_price)
        self.patch_price.start()
        
        # Mock product snapshot retrieval
        def mock_snapshot(product_id):
            name = f"Mock Product {product_id}"
            category = "General Category"
            if product_id == "premium_product":
                name = "Premium Gold Edition Watch"
                category = "Electronics/Watches"
            elif product_id == "budget_product":
                name = "Budget Eco Tee"
                category = "Apparel/T-Shirts"
            return {
                "name": name,
                "category": category,
                "thumbnail": f"https://example.com/assets/{product_id}_thumb.jpg",
                "description": "This is a detailed mock description."
            }
        self.patch_snapshot = patch("services.cart_service.get_product_snapshot", side_effect=mock_snapshot)
        self.patch_snapshot.start()
        
    def tearDown(self):
        self.patcher.stop()
        self.patch_validate.stop()
        self.patch_price.stop()
        self.patch_snapshot.stop()

    def test_get_or_create_cart_exists(self):
        from services.cart_service import get_or_create_cart
        
        existing_cart = {"user_id": "user_exist", "items": [], "price_breakdown": {}}
        self.mock_carts_col.find_one.return_value = existing_cart
        
        result = get_or_create_cart("user_exist")
        self.assertEqual(result, existing_cart)
        self.mock_carts_col.find_one.assert_called_once_with({"user_id": "user_exist"})
        self.mock_carts_col.insert_one.assert_not_called()

    def test_get_or_create_cart_not_exists(self):
        from services.cart_service import get_or_create_cart
        
        self.mock_carts_col.find_one.return_value = None
        
        result = get_or_create_cart("user_new")
        self.assertEqual(result["user_id"], "user_new")
        self.mock_carts_col.insert_one.assert_called_once()

    def test_add_item_new(self):
        from services.cart_service import add_item
        
        cart = create_empty_cart("user_1")
        self.mock_carts_col.find_one.return_value = cart
        
        # Adding product_id="premium_product", base price will be 500
        # quantity=2
        add_item("user_1", "premium_product", {"color": "Gold"}, "Watch Msg", 2)
        
        self.assertEqual(len(cart["items"]), 1)
        item = cart["items"][0]
        self.assertEqual(item["product_id"], "premium_product")
        # Unit price: 500 (base) + 50 (Gold) = 550
        self.assertEqual(item["unit_price"], 550.0)
        self.assertEqual(item["quantity"], 2)
        self.assertEqual(item["line_total"], 1100.0)
        self.assertEqual(cart["price_breakdown"]["subtotal"], 1100.0)
        self.mock_carts_col.replace_one.assert_called_once()

    def test_add_item_duplicate(self):
        from services.cart_service import add_item
        
        cart = create_empty_cart("user_1")
        # Initial item
        cart["items"] = [
            {
                "item_id": "existing-uuid",
                "product_id": "premium_product",
                "quantity": 1,
                "selected_attributes": {"color": "Gold"},
                "custom_text": "Watch Msg",
                "unit_price": 550.0,
                "line_total": 550.0,
                "snapshot": {}
            }
        ]
        self.mock_carts_col.find_one.return_value = cart
        
        # Add duplicate (same product, same attributes, same text)
        add_item("user_1", "premium_product", {"color": "Gold"}, "Watch Msg", 3)
        
        # Quantity should combine to 4
        self.assertEqual(len(cart["items"]), 1)
        self.assertEqual(cart["items"][0]["quantity"], 4)
        self.assertEqual(cart["items"][0]["line_total"], 2200.0)
        self.assertEqual(cart["price_breakdown"]["subtotal"], 2200.0)

    def test_add_item_different_attributes_not_duplicate(self):
        from services.cart_service import add_item
        
        cart = create_empty_cart("user_1")
        cart["items"] = [
            {
                "item_id": "existing-uuid",
                "product_id": "premium_product",
                "quantity": 1,
                "selected_attributes": {"color": "Gold"},
                "custom_text": "Watch Msg",
                "unit_price": 550.0,
                "line_total": 550.0,
                "snapshot": {}
            }
        ]
        self.mock_carts_col.find_one.return_value = cart
        
        # Add item with different attribute (Silver instead of Gold)
        add_item("user_1", "premium_product", {"color": "Silver"}, "Watch Msg", 1)
        
        # Should result in 2 distinct items
        self.assertEqual(len(cart["items"]), 2)
        self.assertEqual(cart["items"][0]["quantity"], 1)
        self.assertEqual(cart["items"][1]["quantity"], 1)

    def test_update_item_quantity_only(self):
        from services.cart_service import update_item
        
        cart = create_empty_cart("user_1")
        item_id = "target-uuid"
        cart["items"] = [
            {
                "item_id": item_id,
                "product_id": "budget_product",
                "quantity": 2,
                "selected_attributes": {"size": "M"},
                "custom_text": "Initial Msg",
                "unit_price": 25.0, # 20 (base) + 5 (M size default surcharge)
                "line_total": 50.0,
                "snapshot": {}
            }
        ]
        self.mock_carts_col.find_one.return_value = cart
        
        # Quantity only change: update to 4
        update_item("user_1", item_id, quantity=4)
        
        self.assertEqual(cart["items"][0]["quantity"], 4)
        # Unit price is preserved (25.0), line total scales
        self.assertEqual(cart["items"][0]["unit_price"], 25.0)
        self.assertEqual(cart["items"][0]["line_total"], 100.0)
        self.assertEqual(cart["price_breakdown"]["subtotal"], 100.0)

    def test_update_item_attributes_reprice(self):
        from services.cart_service import update_item
        
        cart = create_empty_cart("user_1")
        item_id = "target-uuid"
        cart["items"] = [
            {
                "item_id": item_id,
                "product_id": "premium_product",
                "quantity": 1,
                "selected_attributes": {"color": "Silver"}, # surcharge 5
                "custom_text": "Watch Msg",
                "unit_price": 505.0,
                "line_total": 505.0,
                "snapshot": {}
            }
        ]
        self.mock_carts_col.find_one.return_value = cart
        
        # Attribute change: update to color "Gold" (surcharge 50)
        update_item("user_1", item_id, selected_attributes={"color": "Gold"})
        
        self.assertEqual(cart["items"][0]["selected_attributes"], {"color": "Gold"})
        # Unit price should re-price to 550.0 (500 base + 50 Gold)
        self.assertEqual(cart["items"][0]["unit_price"], 550.0)
        self.assertEqual(cart["items"][0]["line_total"], 550.0)
        self.assertEqual(cart["price_breakdown"]["subtotal"], 550.0)

    def test_update_item_merge_on_duplicate(self):
        from services.cart_service import update_item
        
        cart = create_empty_cart("user_1")
        item_a = "uuid-a"
        item_b = "uuid-b"
        cart["items"] = [
            {
                "item_id": item_a,
                "product_id": "premium_product",
                "quantity": 2,
                "selected_attributes": {"color": "Gold"},
                "custom_text": "Watch Msg",
                "unit_price": 550.0,
                "line_total": 1100.0,
                "snapshot": {}
            },
            {
                "item_id": item_b,
                "product_id": "premium_product",
                "quantity": 1,
                "selected_attributes": {"color": "Silver"},
                "custom_text": "Watch Msg",
                "unit_price": 505.0,
                "line_total": 505.0,
                "snapshot": {}
            }
        ]
        self.mock_carts_col.find_one.return_value = cart
        
        # Update item_b attributes to color "Gold", which makes it duplicate of item_a
        update_item("user_1", item_b, selected_attributes={"color": "Gold"})
        
        # item_b should be merged into item_a, leaving 1 item in cart with quantity 3
        self.assertEqual(len(cart["items"]), 1)
        self.assertEqual(cart["items"][0]["item_id"], item_a)
        self.assertEqual(cart["items"][0]["quantity"], 3)
        self.assertEqual(cart["items"][0]["line_total"], 1650.0)

    def test_remove_item(self):
        from services.cart_service import remove_item
        
        cart = create_empty_cart("user_1")
        item_id = "delete-uuid"
        cart["items"] = [
            {
                "item_id": item_id,
                "product_id": "budget_product",
                "quantity": 1,
                "line_total": 20.0,
                "snapshot": {}
            }
        ]
        self.mock_carts_col.find_one.return_value = cart
        
        remove_item("user_1", item_id)
        
        self.assertEqual(len(cart["items"]), 0)
        self.assertEqual(cart["price_breakdown"]["subtotal"], 0.0)

    def test_clear_cart(self):
        from services.cart_service import clear
        
        cart = create_empty_cart("user_1")
        cart["items"] = [
            {"item_id": "1", "line_total": 20.0},
            {"item_id": "2", "line_total": 30.0}
        ]
        self.mock_carts_col.find_one.return_value = cart
        
        clear("user_1")
        
        self.assertEqual(len(cart["items"]), 0)
        self.assertEqual(cart["price_breakdown"]["subtotal"], 0.0)
        self.assertEqual(cart["price_breakdown"]["total"], 0.0)


if __name__ == "__main__":
    unittest.main()
