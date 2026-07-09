import datetime
from bson import ObjectId
from app.db import get_db
from app.utils.cart_snapshot_helper import build_snapshot
from app.mocks.pricing_configurator import validate_attributes, calculate_price

def _decorate_cart(cart):
    if not cart:
        return None
        
    db = get_db()
    items = cart.get("items", [])
    
    decorated_items = []
    subtotal_estimate = 0
    
    for item in items:
        item_copy = dict(item)
        product_id = item_copy.get("product_id")
        
        product = db.products.find_one({"_id": ObjectId(product_id)})
        
        # 1. Product availability checks (inactive/deleted)
        if not product or not product.get("is_active", True):
            item_copy["is_available"] = False
            item_copy["needs_attention"] = False
        else:
            item_copy["is_available"] = True
            
            # 2. Attribute schema change checks
            category_id = product.get("category_id")
            is_valid, errors = validate_attributes(category_id, item_copy.get("selected_attributes", {}))
            if not is_valid:
                item_copy["needs_attention"] = True
                item_copy["validation_errors"] = errors
            else:
                item_copy["needs_attention"] = False
                
        # Only add to subtotal estimate if the item is available
        if item_copy.get("is_available", True):
            subtotal_estimate += item_copy.get("line_total_estimate", 0)
            
        decorated_items.append(item_copy)
        
    # Build decorated cart response shape
    decorated_cart = {
        "_id": cart["_id"],
        "user_id": cart["user_id"],
        "items": decorated_items,
        "item_count": sum(item.get("quantity", 0) for item in decorated_items),
        "subtotal_estimate": subtotal_estimate,
        "updated_at": cart.get("updated_at")
    }
    return decorated_cart

def get_or_create_cart(user_id):
    """
    Fetches the cart for the user or creates a new empty cart if missing.
    Dynamic read-time stale flags are computed and populated.
    """
    db = get_db()
    user_oid = ObjectId(user_id)
    cart = db.carts.find_one({"user_id": user_oid})
    if not cart:
        now = datetime.datetime.now(datetime.timezone.utc)
        new_cart = {
            "user_id": user_oid,
            "items": [],
            "updated_at": now
        }
        db.carts.insert_one(new_cart)
        cart = db.carts.find_one({"user_id": user_oid})
    return _decorate_cart(cart)

def add_item(user_id, item_data):
    """
    Adds a custom or pre-designed item to the user's cart.
    Validates selected attributes and pricing.
    Merges duplicate line items.
    """
    db = get_db()
    user_oid = ObjectId(user_id)
    
    product_id_str = item_data.get("product_id")
    if not product_id_str:
        raise ValueError("Product ID is required")
        
    product_id = ObjectId(product_id_str)
    product = db.products.find_one({"_id": product_id})
    if not product or not product.get("is_active", True):
        raise FileNotFoundError("Product not found or is inactive")
        
    selected_attributes = item_data.get("selected_attributes", {})
    quantity = item_data.get("quantity", 1)
    if not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Quantity must be a positive integer")
        
    custom_text = item_data.get("custom_text")
    ai_preview_image = item_data.get("ai_preview_image")
    
    # Validate attributes selection
    category_id = product.get("category_id")
    is_valid, errors = validate_attributes(category_id, selected_attributes)
    if not is_valid:
        raise ValueError({"message": "Invalid attributes selection", "errors": errors})
        
    # Calculate price fresh
    unit_price, price_breakdown = calculate_price(product, selected_attributes)
    line_total = unit_price * quantity
    
    # Build snapshot fields
    snapshot = build_snapshot(product_id)
    
    cart = db.carts.find_one({"user_id": user_oid})
    if not cart:
        now = datetime.datetime.now(datetime.timezone.utc)
        db.carts.insert_one({
            "user_id": user_oid,
            "items": [],
            "updated_at": now
        })
        cart = db.carts.find_one({"user_id": user_oid})
        
    items = cart.get("items", [])
    
    # Check if duplicate item exists
    duplicate_found = False
    for item in items:
        if (ObjectId(item["product_id"]) == product_id and 
            item.get("selected_attributes") == selected_attributes and 
            item.get("custom_text") == custom_text):
            
            # Increment quantity
            item["quantity"] += quantity
            item["unit_price_estimate"] = unit_price
            item["line_total_estimate"] = item["unit_price_estimate"] * item["quantity"]
            item["price_breakdown"] = price_breakdown
            item["updated_at"] = datetime.datetime.now(datetime.timezone.utc)
            duplicate_found = True
            break
            
    if not duplicate_found:
        now = datetime.datetime.now(datetime.timezone.utc)
        new_item = {
            "_id": ObjectId(),
            "product_id": product_id,
            "category_id": ObjectId(snapshot["category_id"]),
            "product_title": snapshot["product_title"],
            "category_name": snapshot["category_name"],
            "thumbnail": snapshot["thumbnail"],
            "selected_attributes": selected_attributes,
            "quantity": quantity,
            "unit_price_estimate": unit_price,
            "line_total_estimate": line_total,
            "price_breakdown": price_breakdown,
            "ai_preview_image": ai_preview_image,
            "custom_text": custom_text,
            "added_at": now,
            "updated_at": now
        }
        items.append(new_item)
        
    db.carts.update_one(
        {"user_id": user_oid},
        {
            "$set": {
                "items": items,
                "updated_at": datetime.datetime.now(datetime.timezone.utc)
            }
        }
    )
    
    updated_cart = db.carts.find_one({"user_id": user_oid})
    return _decorate_cart(updated_cart)

def update_item(user_id, item_id_str, update_data):
    """
    Updates configuration or quantity of an existing item in the cart.
    Re-validates attributes and recalculates pricing if changed.
    """
    db = get_db()
    user_oid = ObjectId(user_id)
    item_id = ObjectId(item_id_str)
    
    cart = db.carts.find_one({"user_id": user_oid})
    if not cart:
        raise FileNotFoundError("Cart not found")
        
    items = cart.get("items", [])
    item_to_update = None
    for item in items:
        if ObjectId(item["_id"]) == item_id:
            item_to_update = item
            break
            
    if not item_to_update:
        raise FileNotFoundError("Item not found in cart")
        
    quantity = update_data.get("quantity")
    selected_attributes = update_data.get("selected_attributes")
    custom_text = update_data.get("custom_text")
    ai_preview_image = update_data.get("ai_preview_image")
    
    # Check if attributes or custom text are modified
    attributes_changed = (selected_attributes is not None and selected_attributes != item_to_update.get("selected_attributes"))
    custom_text_changed = (custom_text is not None and custom_text != item_to_update.get("custom_text"))
    
    if quantity is not None:
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        item_to_update["quantity"] = quantity
        
    if attributes_changed or custom_text_changed:
        product_id = ObjectId(item_to_update["product_id"])
        product = db.products.find_one({"_id": product_id})
        if not product:
            raise FileNotFoundError("Product not found")
            
        new_attrs = selected_attributes if selected_attributes is not None else item_to_update.get("selected_attributes", {})
        category_id = product.get("category_id")
        
        # Re-validate
        is_valid, errors = validate_attributes(category_id, new_attrs)
        if not is_valid:
            raise ValueError({"message": "Invalid attributes selection", "errors": errors})
            
        # Re-price
        unit_price, price_breakdown = calculate_price(product, new_attrs)
        item_to_update["selected_attributes"] = new_attrs
        item_to_update["unit_price_estimate"] = unit_price
        item_to_update["price_breakdown"] = price_breakdown
        if custom_text is not None:
            item_to_update["custom_text"] = custom_text
            
    if ai_preview_image is not None:
        item_to_update["ai_preview_image"] = ai_preview_image
        
    # Recalculate line total
    item_to_update["line_total_estimate"] = item_to_update["unit_price_estimate"] * item_to_update["quantity"]
    item_to_update["updated_at"] = datetime.datetime.now(datetime.timezone.utc)
    
    # Check if the update creates a duplicate of another item in the cart
    duplicate_item = None
    for other_item in items:
        if ObjectId(other_item["_id"]) != item_id:
            if (ObjectId(other_item["product_id"]) == ObjectId(item_to_update["product_id"]) and 
                other_item.get("selected_attributes") == item_to_update.get("selected_attributes") and 
                other_item.get("custom_text") == item_to_update.get("custom_text")):
                duplicate_item = other_item
                break
                
    if duplicate_item:
        duplicate_item["quantity"] += item_to_update["quantity"]
        duplicate_item["line_total_estimate"] = duplicate_item["unit_price_estimate"] * duplicate_item["quantity"]
        duplicate_item["updated_at"] = datetime.datetime.now(datetime.timezone.utc)
        items.remove(item_to_update)
        
    db.carts.update_one(
        {"user_id": user_oid},
        {
            "$set": {
                "items": items,
                "updated_at": datetime.datetime.now(datetime.timezone.utc)
            }
        }
    )
    
    updated_cart = db.carts.find_one({"user_id": user_oid})
    return _decorate_cart(updated_cart)

def remove_item(user_id, item_id_str):
    """
    Removes an item from the cart.
    """
    db = get_db()
    user_oid = ObjectId(user_id)
    item_id = ObjectId(item_id_str)
    
    cart = db.carts.find_one({"user_id": user_oid})
    if not cart:
        raise FileNotFoundError("Cart not found")
        
    items = cart.get("items", [])
    item_to_remove = None
    for item in items:
        if ObjectId(item["_id"]) == item_id:
            item_to_remove = item
            break
            
    if not item_to_remove:
        raise FileNotFoundError("Item not found in cart")
        
    items.remove(item_to_remove)
    
    db.carts.update_one(
        {"user_id": user_oid},
        {
            "$set": {
                "items": items,
                "updated_at": datetime.datetime.now(datetime.timezone.utc)
            }
        }
    )
    
    updated_cart = db.carts.find_one({"user_id": user_oid})
    return _decorate_cart(updated_cart)

def clear(user_id):
    """
    Clears all items from the user's cart.
    """
    db = get_db()
    user_oid = ObjectId(user_id)
    
    cart = db.carts.find_one({"user_id": user_oid})
    if not cart:
        db.carts.insert_one({
            "user_id": user_oid,
            "items": [],
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        })
    else:
        db.carts.update_one(
            {"user_id": user_oid},
            {
                "$set": {
                    "items": [],
                    "updated_at": datetime.datetime.now(datetime.timezone.utc)
                }
            }
        )
        
    updated_cart = db.carts.find_one({"user_id": user_oid})
    return _decorate_cart(updated_cart)
