from flask import Blueprint, request, jsonify, g
from bson import ObjectId
from app.db import db
from app.middleware.auth import require_auth
from app.services.config_service import ConfigService
import datetime

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("", methods=["GET"])
@require_auth
def get_cart():
    user_id = g.user["id"]
    cart = db.carts.find_one({"user_id": ObjectId(user_id)})
    
    if not cart:
        # Create empty cart for convenience
        cart = {"user_id": ObjectId(user_id), "items": [], "updated_at": datetime.datetime.utcnow()}
        db.carts.insert_one(cart)
        
    items = cart.get("items", [])
    updated_items = []
    
    # Validation loop for availability and stock changes (stale item checking)
    for item in items:
        prod_id = item.get("product_id")
        product = db.products.find_one({"_id": prod_id})
        
        is_available = True
        needs_attention = False
        message = ""
        
        if not product or not product.get("is_active", True):
            is_available = False
            message = "Product is no longer available."
        elif product.get("stock_status") == "out_of_stock":
            is_available = False
            message = "Product is currently out of stock."
            
        # Re-verify pricing just in case prices changed
        pricing, err = ConfigService.calculate_price(str(prod_id), item.get("selected_attributes", {}))
        if err:
            is_available = False
            message = f"Configuration error: {err}"
        else:
            current_price = pricing["total_price"]
            if current_price != item.get("unit_price_estimate"):
                item["unit_price_estimate"] = current_price
                needs_attention = True
                message = "Pricing for this item has been updated."
                
        item["is_available"] = is_available
        item["needs_attention"] = needs_attention
        item["message"] = message
        
        # Serialize ObjectIds for JSON
        if "id" in item:
            item["id"] = str(item["id"])
        item["product_id"] = str(item["product_id"])
        item["category_id"] = str(item["category_id"])
        if "added_at" in item:
            item["added_at"] = item["added_at"].isoformat()
            
        updated_items.append(item)
        
    # Save back validated items
    db.carts.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": {"items": cart["items"], "updated_at": datetime.datetime.utcnow()}}
    )
    
    return jsonify({
        "success": True,
        "data": {
            "items": updated_items
        }
    }), 200

@cart_bp.route("/items", methods=["POST"])
@require_auth
def add_cart_item():
    user_id = g.user["id"]
    data = request.get_json() or {}
    product_id_str = data.get("product_id")
    selected_attributes = data.get("selected_attributes", {})
    quantity = data.get("quantity", 1)
    ai_preview_image = data.get("ai_preview_image")
    custom_text = data.get("custom_text", "")
    
    if not product_id_str:
        return jsonify({"success": False, "message": "product_id is required"}), 400
        
    # Get product & validate schema
    product = db.products.find_one({"_id": ObjectId(product_id_str), "is_active": True})
    if not product:
        return jsonify({"success": False, "message": "Product not found or inactive"}), 404
        
    category_id_str = str(product["category_id"])
    
    # Validate selected attributes
    is_valid, msg, validated_attrs = ConfigService.validate_attributes(category_id_str, selected_attributes)
    if not is_valid:
        return jsonify({"success": False, "message": msg, "errors": validated_attrs}), 422
        
    # Calculate price
    pricing, err = ConfigService.calculate_price(product_id_str, validated_attrs)
    if err:
        return jsonify({"success": False, "message": err}), 400
        
    unit_price = pricing["total_price"]
    
    cart_item = {
        "id": ObjectId(),
        "product_id": ObjectId(product_id_str),
        "category_id": ObjectId(category_id_str),
        "selected_attributes": validated_attrs,
        "quantity": int(quantity),
        "unit_price_estimate": unit_price,
        "ai_preview_image": ai_preview_image,
        "custom_text": custom_text,
        "added_at": datetime.datetime.utcnow()
    }
    
    cart = db.carts.find_one({"user_id": ObjectId(user_id)})
    if not cart:
        cart = {"user_id": ObjectId(user_id), "items": [], "updated_at": datetime.datetime.utcnow()}
        db.carts.insert_one(cart)
        
    items = cart.get("items", [])
    
    # Check if identical item (same product ID + attributes) is already in cart
    item_found = False
    for item in items:
        if str(item.get("product_id")) == product_id_str and item.get("selected_attributes") == validated_attrs:
            item["quantity"] += int(quantity)
            item["added_at"] = datetime.datetime.utcnow()
            item_found = True
            break
            
    if not item_found:
        items.append(cart_item)
        
    db.carts.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": {"items": items, "updated_at": datetime.datetime.utcnow()}}
    )
    
    return jsonify({
        "success": True,
        "message": "Item added to cart successfully"
    }), 201

@cart_bp.route("/items/<item_id>", methods=["PUT"])
@require_auth
def update_cart_item(item_id):
    # In MongoDB, the array doesn't have an auto ObjectId, but we can treat item_id as index 
    # or identify by product_id_str. 
    # For Next.js/React, let's identify the item by index or pass product_id + attributes to target it.
    # Let's support targeting via product_id since custom attributes define uniqueness.
    # Alternatively, we can assign an 'id' (ObjectId) to each cart item when creating it!
    # Let's make sure our cart_item generation assigns a unique "id" field: ObjectId()! 
    # That is extremely clean and standard. Let's add that logic.
    user_id = g.user["id"]
    data = request.get_json() or {}
    quantity = data.get("quantity")
    
    cart = db.carts.find_one({"user_id": ObjectId(user_id)})
    if not cart:
        return jsonify({"success": False, "message": "Cart not found"}), 404
        
    items = cart.get("items", [])
    target_item = None
    for item in items:
        # Check if item has 'id' matching item_id string
        if str(item.get("id")) == item_id:
            target_item = item
            break
            
    if not target_item:
        # Fallback to index if item_id is numeric
        try:
            idx = int(item_id)
            if 0 <= idx < len(items):
                target_item = items[idx]
        except ValueError:
            return jsonify({"success": False, "message": "Cart item not found"}), 404
            
    if not target_item:
        return jsonify({"success": False, "message": "Cart item not found"}), 404
        
    if quantity is not None:
        target_item["quantity"] = int(quantity)
        
    db.carts.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": {"items": items, "updated_at": datetime.datetime.utcnow()}}
    )
    
    return jsonify({"success": True, "message": "Cart item updated successfully"}), 200

@cart_bp.route("/items/<item_id>", methods=["DELETE"])
@require_auth
def delete_cart_item(item_id):
    user_id = g.user["id"]
    cart = db.carts.find_one({"user_id": ObjectId(user_id)})
    if not cart:
        return jsonify({"success": False, "message": "Cart not found"}), 404
        
    items = cart.get("items", [])
    original_len = len(items)
    
    # Filter out target
    items = [item for item in items if str(item.get("id")) != item_id]
    
    # Fallback to index if not deleted
    if len(items) == original_len:
        try:
            idx = int(item_id)
            if 0 <= idx < len(items):
                items.pop(idx)
        except ValueError:
            pass
            
    db.carts.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": {"items": items, "updated_at": datetime.datetime.utcnow()}}
    )
    
    return jsonify({"success": True, "message": "Cart item removed successfully"}), 200

@cart_bp.route("/clear", methods=["DELETE"])
@require_auth
def clear_cart():
    user_id = g.user["id"]
    db.carts.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": {"items": [], "updated_at": datetime.datetime.utcnow()}}
    )
    return jsonify({"success": True, "message": "Cart cleared successfully"}), 200
