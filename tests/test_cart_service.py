import pytest
from bson import ObjectId
from app.services import cart_service
from app.db import get_db

def test_get_or_create_cart_new(db):
    user_id = ObjectId()
    cart = cart_service.get_or_create_cart(user_id)
    assert cart is not None
    assert cart["user_id"] == user_id
    assert len(cart["items"]) == 0
    assert cart["item_count"] == 0
    assert cart["subtotal_estimate"] == 0

def test_add_item_success(seed_data):
    user_id = ObjectId()
    item_data = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 2,
        "selected_attributes": {
            "font": "bold",
            "color": "blue"
        },
        "custom_text": "Hello Neon"
    }
    
    cart = cart_service.add_item(user_id, item_data)
    assert len(cart["items"]) == 1
    item = cart["items"][0]
    
    # Check snapshot fields
    assert item["product_title"] == "Custom Neon Sign"
    assert item["category_name"] == "Neon Boards"
    assert item["thumbnail"] == "http://res.cloudinary.com/test/neon.jpg"
    
    # Check pricing calculations
    # base 1500 + bold 150 + blue 100 = 1750
    assert item["unit_price_estimate"] == 1750
    assert item["quantity"] == 2
    assert item["line_total_estimate"] == 3500
    
    assert cart["item_count"] == 2
    assert cart["subtotal_estimate"] == 3500

def test_add_item_duplicate_merging(seed_data):
    user_id = ObjectId()
    item_data = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 2,
        "selected_attributes": {
            "font": "bold",
            "color": "blue"
        },
        "custom_text": "Hello Neon"
    }
    
    # Add first time
    cart = cart_service.add_item(user_id, item_data)
    # Add identical item second time
    cart = cart_service.add_item(user_id, item_data)
    
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 4
    assert cart["items"][0]["line_total_estimate"] == 7000
    
    # Add with different attributes (color: pink instead of blue)
    item_data_diff = dict(item_data)
    item_data_diff["selected_attributes"] = {
        "font": "bold",
        "color": "pink"
    }
    cart = cart_service.add_item(user_id, item_data_diff)
    
    # Should create a separate line item since attributes differ
    assert len(cart["items"]) == 2

def test_add_item_inactive_product(seed_data):
    user_id = ObjectId()
    item_data = {
        "product_id": str(seed_data["product_inactive_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "bold",
            "color": "pink"
        }
    }
    with pytest.raises(FileNotFoundError):
        cart_service.add_item(user_id, item_data)

def test_add_item_invalid_attributes(seed_data):
    user_id = ObjectId()
    
    # 1. Missing required field "font"
    item_data_missing = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "color": "blue"
        }
    }
    with pytest.raises(ValueError) as excinfo:
        cart_service.add_item(user_id, item_data_missing)
    assert "font" in excinfo.value.args[0]["errors"]
    
    # 2. Invalid option for "color"
    item_data_invalid_opt = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "cursive",
            "color": "green" # Green is not a seeded option
        }
    }
    with pytest.raises(ValueError) as excinfo:
        cart_service.add_item(user_id, item_data_invalid_opt)
    assert "color" in excinfo.value.args[0]["errors"]

def test_update_item_quantity(seed_data):
    user_id = ObjectId()
    item_data = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "cursive",
            "color": "pink"
        }
    }
    cart = cart_service.add_item(user_id, item_data)
    item_id = cart["items"][0]["_id"]
    
    # Update quantity to 3
    updated_cart = cart_service.update_item(user_id, item_id, {"quantity": 3})
    assert updated_cart["items"][0]["quantity"] == 3
    assert updated_cart["items"][0]["line_total_estimate"] == 1500 * 3 # 1500 is base price (cursive/pink are 0 price delta)
    assert updated_cart["subtotal_estimate"] == 4500

def test_update_item_attributes(seed_data):
    user_id = ObjectId()
    item_data = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "cursive",
            "color": "pink"
        }
    }
    cart = cart_service.add_item(user_id, item_data)
    item_id = cart["items"][0]["_id"]
    
    # Update attributes (change font to bold, color to blue)
    # Price should change: 1500 base + 150 bold + 100 blue = 1750
    updated_cart = cart_service.update_item(user_id, item_id, {
        "selected_attributes": {
            "font": "bold",
            "color": "blue"
        }
    })
    
    assert updated_cart["items"][0]["unit_price_estimate"] == 1750
    assert updated_cart["items"][0]["line_total_estimate"] == 1750

def test_update_item_invalid_quantity(seed_data):
    user_id = ObjectId()
    item_data = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "cursive",
            "color": "pink"
        }
    }
    cart = cart_service.add_item(user_id, item_data)
    item_id = cart["items"][0]["_id"]
    
    # Negative quantity should fail
    with pytest.raises(ValueError):
        cart_service.update_item(user_id, item_id, {"quantity": -1})
        
    # Zero quantity should fail
    with pytest.raises(ValueError):
        cart_service.update_item(user_id, item_id, {"quantity": 0})

def test_remove_item(seed_data):
    user_id = ObjectId()
    item_data = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "cursive",
            "color": "pink"
        }
    }
    cart = cart_service.add_item(user_id, item_data)
    item_id = cart["items"][0]["_id"]
    
    updated_cart = cart_service.remove_item(user_id, item_id)
    assert len(updated_cart["items"]) == 0

def test_clear_cart(seed_data):
    user_id = ObjectId()
    item_data = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "cursive",
            "color": "pink"
        }
    }
    cart_service.add_item(user_id, item_data)
    
    updated_cart = cart_service.clear(user_id)
    assert len(updated_cart["items"]) == 0

def test_stale_product_handling(seed_data, db):
    user_id = ObjectId()
    item_data = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "cursive",
            "color": "pink"
        }
    }
    cart_service.add_item(user_id, item_data)
    
    # 1. Initially it should be available
    cart = cart_service.get_or_create_cart(user_id)
    assert cart["items"][0]["is_available"] is True
    assert cart["subtotal_estimate"] == 1500
    
    # 2. Deactivate the product
    db.products.update_one(
        {"_id": ObjectId(seed_data["product_active_id"])},
        {"$set": {"is_active": False}}
    )
    
    # 3. Dynamic stale checks on fetch should show it as unavailable
    cart = cart_service.get_or_create_cart(user_id)
    assert cart["items"][0]["is_available"] is False
    # Subtotal estimate should now exclude the unavailable item
    assert cart["subtotal_estimate"] == 0

def test_stale_attribute_schema_handling(seed_data, db):
    user_id = ObjectId()
    item_data = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "bold",
            "color": "pink"
        }
    }
    cart_service.add_item(user_id, item_data)
    
    # 1. Initially it should not need attention
    cart = cart_service.get_or_create_cart(user_id)
    assert cart["items"][0]["needs_attention"] is False
    
    # 2. Alter the category schema so "bold" is no longer an allowed font
    db.categories.update_one(
        {"_id": ObjectId(seed_data["category_id"])},
        {
            "$set": {
                "attribute_schema.0.options": [
                    {"value": "cursive", "label": "Cursive", "price_delta": 0}
                ]
            }
        }
    )
    
    # 3. Dynamic stale checks should flag this item as needing attention
    cart = cart_service.get_or_create_cart(user_id)
    assert cart["items"][0]["needs_attention"] is True
    assert "font" in cart["items"][0]["validation_errors"]

def test_update_item_duplicate_merging(seed_data):
    user_id = ObjectId()
    # Add first item (color: blue)
    item_data_1 = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 2,
        "selected_attributes": {
            "font": "bold",
            "color": "blue"
        },
        "custom_text": "Hello Neon"
    }
    cart = cart_service.add_item(user_id, item_data_1)
    
    # Add second item (color: pink)
    item_data_2 = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 3,
        "selected_attributes": {
            "font": "bold",
            "color": "pink"
        },
        "custom_text": "Hello Neon"
    }
    cart = cart_service.add_item(user_id, item_data_2)
    
    assert len(cart["items"]) == 2
    
    # Get the ID of the pink item to update it
    pink_item_id = None
    for item in cart["items"]:
        if item["selected_attributes"]["color"] == "pink":
            pink_item_id = item["_id"]
            break
            
    assert pink_item_id is not None
    
    # Update the pink item's color to blue (matching the first item)
    updated_cart = cart_service.update_item(user_id, pink_item_id, {
        "selected_attributes": {
            "font": "bold",
            "color": "blue"
        }
    })
    
    # Should merge the updated item into the first one
    assert len(updated_cart["items"]) == 1
    assert updated_cart["items"][0]["quantity"] == 5  # 2 (blue) + 3 (pink updated to blue)
    assert updated_cart["items"][0]["selected_attributes"]["color"] == "blue"

def test_checkout_contract_integration(seed_data):
    user_id = ObjectId()
    item_data = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "cursive",
            "color": "pink"
        }
    }
    cart_service.add_item(user_id, item_data)
    
    # Simulate Module 8 retrieving the cart during checkout flow
    checkout_cart = cart_service.get_or_create_cart(user_id)
    assert len(checkout_cart["items"]) == 1
    assert checkout_cart["items"][0]["product_title"] == "Custom Neon Sign"
    
    # Simulate successful checkout and Module 8 calling cart_service.clear(user_id)
    cleared_cart = cart_service.clear(user_id)
    assert len(cleared_cart["items"]) == 0

