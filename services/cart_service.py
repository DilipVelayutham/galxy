import datetime
from pymongo.errors import DuplicateKeyError
from db import db
from models.cart import (
    create_empty_cart,
    construct_cart_item,
    are_items_duplicate,
    recalculate_cart_totals,
    to_object_id
)

# Import real implementations of Module 4 & 5 configurator and catalog services
from services.configurator_service import validate_attributes, calculate_price
from services.product_service import get_product_snapshot

def get_or_create_cart(user_id):
    """
    Retrieve the cart for the given user_id. If none exists, create an empty cart.
    Ensures a 404 is never returned.
    
    Importable for Module 8:
        from services.cart_service import get_or_create_cart
    """
    if not user_id:
        raise ValueError("user_id must be provided.")
        
    # Standardize user_id format (store as string to keep consistent)
    user_id_str = str(user_id)
    
    cart = db.carts.find_one({"user_id": user_id_str})
    if not cart:
        # Create empty cart
        cart = create_empty_cart(user_id_str)
        try:
            db.carts.insert_one(cart)
        except DuplicateKeyError:
            # Handle race conditions where another thread created the cart in parallel
            cart = db.carts.find_one({"user_id": user_id_str})
            
    return cart

def add_item(user_id, product_id, selected_attributes, custom_text, quantity):
    """
    Validates attributes & fetches fresh price from Module 4.
    Fetches catalog details from Module 5 for the snapshot.
    Applies the duplicate item rule to increment quantity if the item already exists.
    Saves and returns the updated cart.
    """
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")
        
    product_id_str = str(product_id)
    selected_attributes = selected_attributes or {}
    custom_text = (custom_text or "").strip()

    # Fetch product from DB to find category_id
    prod_id = to_object_id(product_id_str)
    product = db.products.find_one({"_id": prod_id})
    if not product:
        raise ValueError(f"Product with ID {product_id_str} not found in catalog.")
    category_id = str(product.get("category_id", ""))

    # Step 1: Validate attributes via Module 4 (Pricing & Validation Layer)
    validate_attributes(category_id, selected_attributes)

    # Step 2: Fetch price breakdown from Module 4
    price_info = calculate_price(product_id_str, selected_attributes)
    unit_price = price_info["unit_price"]

    # Step 3: Fetch Catalog snapshot from Module 5
    snapshot = get_product_snapshot(product_id_str)

    # Step 4: Get/Create Cart
    cart = get_or_create_cart(user_id)
    
    # Step 5: Duplicate Rule Check
    # Construct a temp item for duplicate matching
    new_item_candidate = construct_cart_item(
        product_id=product_id_str,
        quantity=quantity,
        selected_attributes=selected_attributes,
        custom_text=custom_text,
        unit_price=unit_price,
        snapshot=snapshot
    )
    
    duplicate_found = False
    for existing_item in cart["items"]:
        if are_items_duplicate(existing_item, new_item_candidate):
            # Same item -> Increment quantity and recalculate its line total
            existing_item["quantity"] += quantity
            existing_item["line_total"] = round(existing_item["unit_price"] * existing_item["quantity"], 2)
            duplicate_found = True
            break
            
    if not duplicate_found:
        # Different item -> Append the new line item
        cart["items"].append(new_item_candidate)

    # Step 6: Recalculate cart totals and update database
    recalculate_cart_totals(cart)
    db.carts.replace_one({"user_id": cart["user_id"]}, cart)
    
    return cart

def update_item(user_id, item_id, quantity=None, selected_attributes=None, custom_text=None):
    """
    Updates a specific cart item.
    - Re-validates and re-prices if attributes or custom text changes.
    - If only quantity changes, re-prices using stored attributes and scales the line total.
    - Merges items if the update turns it into a duplicate of another item in the cart.
    - Rejects quantity <= 0.
    """
    cart = get_or_create_cart(user_id)
    
    # Find the target item by item_id
    target_idx = None
    for idx, item in enumerate(cart.get("items", [])):
        if item.get("item_id") == item_id:
            target_idx = idx
            break
            
    if target_idx is None:
        raise ValueError(f"Item with ID {item_id} not found in cart.")
        
    target_item = cart["items"][target_idx]
    
    # Determine what's changing
    attr_changed = (selected_attributes is not None) and (selected_attributes != target_item["selected_attributes"])
    text_changed = (custom_text is not None) and (custom_text.strip() != target_item["custom_text"])
    qty_changed = (quantity is not None) and (quantity != target_item["quantity"])
    
    if qty_changed and quantity <= 0:
        raise ValueError("Quantity must be greater than zero. To remove, use remove_item.")

    # Re-validate and re-price if attributes or custom text change
    if attr_changed or text_changed:
        updated_attrs = selected_attributes if selected_attributes is not None else target_item["selected_attributes"]
        updated_text = custom_text if custom_text is not None else target_item["custom_text"]
        
        # Verify attributes using Module 4
        prod_id = to_object_id(target_item["product_id"])
        product = db.products.find_one({"_id": prod_id})
        if not product:
            raise ValueError(f"Product with ID {target_item['product_id']} not found in catalog.")
        category_id = str(product.get("category_id", ""))
        validate_attributes(category_id, updated_attrs)
        
        # Recalculate price using Module 4
        price_info = calculate_price(target_item["product_id"], updated_attrs)
        unit_price = price_info["unit_price"]
        
        # Apply changes
        target_item["selected_attributes"] = updated_attrs
        target_item["custom_text"] = updated_text.strip()
        target_item["unit_price"] = round(float(unit_price), 2)
        
    # Update quantity
    if qty_changed:
        target_item["quantity"] = int(quantity)
        
    # Scale line_total using the updated/existing unit price
    target_item["line_total"] = round(target_item["unit_price"] * target_item["quantity"], 2)

    # If attributes or custom text changed, we may have created a duplicate of an existing item in the cart.
    # Check if we should merge target_item into another item.
    if attr_changed or text_changed:
        merge_idx = None
        for idx, item in enumerate(cart["items"]):
            if idx != target_idx and are_items_duplicate(item, target_item):
                merge_idx = idx
                break
                
        if merge_idx is not None:
            # Merge target item into the existing matching item
            cart["items"][merge_idx]["quantity"] += target_item["quantity"]
            cart["items"][merge_idx]["line_total"] = round(
                cart["items"][merge_idx]["unit_price"] * cart["items"][merge_idx]["quantity"], 2
            )
            # Remove the current target item from the list
            cart["items"].pop(target_idx)

    # Recalculate cart totals and update database
    recalculate_cart_totals(cart)
    db.carts.replace_one({"user_id": cart["user_id"]}, cart)
    
    return cart

def remove_item(user_id, item_id):
    """
    Removes an item from the cart, recalculates totals, and saves changes.
    """
    cart = get_or_create_cart(user_id)
    
    initial_len = len(cart.get("items", []))
    cart["items"] = [item for item in cart.get("items", []) if item.get("item_id") != item_id]
    
    if len(cart["items"]) == initial_len:
        raise ValueError(f"Item with ID {item_id} not found in cart.")
        
    recalculate_cart_totals(cart)
    db.carts.replace_one({"user_id": cart["user_id"]}, cart)
    
    return cart

def clear(user_id):
    """
    Empties the cart's items and resets the price breakdown. Called after checkout by Module 8.
    """
    cart = get_or_create_cart(user_id)
    
    cart["items"] = []
    recalculate_cart_totals(cart)
    
    db.carts.replace_one({"user_id": cart["user_id"]}, cart)
    
    return cart
