import json
from bson import ObjectId

def test_route_unauthorized(client):
    # Missing auth header
    res = client.get("/api/cart")
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False
    assert "Authentication required" in data["message"]
    
    # Invalid user ID format
    res = client.get("/api/cart", headers={"X-User-Id": "not-an-object-id"})
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False
    assert "Invalid user ID format" in data["message"]

def test_route_get_cart(client):
    user_id = str(ObjectId())
    res = client.get("/api/cart", headers={"X-User-Id": user_id})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["user_id"] == user_id
    assert len(data["data"]["items"]) == 0

def test_route_add_item_success(client, seed_data):
    user_id = str(ObjectId())
    payload = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 2,
        "selected_attributes": {
            "font": "cursive",
            "color": "blue"
        },
        "custom_text": "Custom Neon"
    }
    
    res = client.post(
        "/api/cart/items",
        headers={"X-User-Id": user_id},
        json=payload
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["message"] == "Added to cart"
    assert len(data["data"]["items"]) == 1
    assert data["data"]["items"][0]["quantity"] == 2
    assert data["data"]["items"][0]["unit_price_estimate"] == 1600 # base 1500 + blue 100

def test_route_add_item_invalid_attributes(client, seed_data):
    user_id = str(ObjectId())
    payload = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "bold",
            "color": "orange" # orange is invalid color option
        }
    }
    
    res = client.post(
        "/api/cart/items",
        headers={"X-User-Id": user_id},
        json=payload
    )
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert data["message"] == "Invalid attributes selection"
    assert "color" in data["errors"]

def test_route_add_item_not_found(client):
    user_id = str(ObjectId())
    payload = {
        "product_id": str(ObjectId()), # Random ObjectId
        "quantity": 1,
        "selected_attributes": {}
    }
    
    res = client.post(
        "/api/cart/items",
        headers={"X-User-Id": user_id},
        json=payload
    )
    assert res.status_code == 404
    data = res.get_json()
    assert data["success"] is False

def test_route_update_item_success(client, seed_data):
    user_id = str(ObjectId())
    
    # 1. Add item
    add_payload = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "cursive",
            "color": "pink"
        }
    }
    add_res = client.post(
        "/api/cart/items",
        headers={"X-User-Id": user_id},
        json=add_payload
    )
    assert add_res.status_code == 201
    item_id = add_res.get_json()["data"]["items"][0]["_id"]
    
    # 2. Update item quantity and custom text
    update_payload = {
        "quantity": 5,
        "custom_text": "Updated Custom Text"
    }
    update_res = client.put(
        f"/api/cart/items/{item_id}",
        headers={"X-User-Id": user_id},
        json=update_payload
    )
    assert update_res.status_code == 200
    update_data = update_res.get_json()
    assert update_data["success"] is True
    updated_item = update_data["data"]["items"][0]
    assert updated_item["quantity"] == 5
    assert updated_item["custom_text"] == "Updated Custom Text"
    assert updated_item["line_total_estimate"] == 1500 * 5

def test_route_remove_item_success(client, seed_data):
    user_id = str(ObjectId())
    
    # 1. Add item
    add_payload = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "cursive",
            "color": "pink"
        }
    }
    add_res = client.post(
        "/api/cart/items",
        headers={"X-User-Id": user_id},
        json=add_payload
    )
    item_id = add_res.get_json()["data"]["items"][0]["_id"]
    
    # 2. Remove item
    remove_res = client.delete(
        f"/api/cart/items/{item_id}",
        headers={"X-User-Id": user_id}
    )
    assert remove_res.status_code == 200
    remove_data = remove_res.get_json()
    assert remove_data["success"] is True
    assert remove_data["message"] == "Item removed"
    assert len(remove_data["data"]["items"]) == 0

def test_route_clear_cart_success(client, seed_data):
    user_id = str(ObjectId())
    
    # 1. Add item
    add_payload = {
        "product_id": str(seed_data["product_active_id"]),
        "quantity": 1,
        "selected_attributes": {
            "font": "cursive",
            "color": "pink"
        }
    }
    client.post(
        "/api/cart/items",
        headers={"X-User-Id": user_id},
        json=add_payload
    )
    
    # 2. Clear cart
    clear_res = client.delete(
        "/api/cart/clear",
        headers={"X-User-Id": user_id}
    )
    assert clear_res.status_code == 200
    clear_data = clear_res.get_json()
    assert clear_data["success"] is True
    assert clear_data["message"] == "Cart cleared"
    assert len(clear_data["data"]["items"]) == 0
