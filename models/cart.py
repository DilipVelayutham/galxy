import datetime
import uuid
from bson import ObjectId

def init_cart_indexes(db):
    """
    Initializes database indexes for the carts collection.
    Ensures that a user can only have one active cart (unique index on user_id).
    """
    db.carts.create_index("user_id", unique=True)

def to_object_id(val):
    """
    Helper to convert a string representation to a BSON ObjectId if valid.
    Otherwise returns the original value.
    """
    if not val:
        return None
    if isinstance(val, ObjectId):
        return val
    try:
        return ObjectId(str(val))
    except Exception:
        return val

def serialize_doc(doc):
    """
    Recursively normalizes a MongoDB document to make it JSON serializable.
    Converts ObjectIds to strings and datetimes to ISO format strings.
    """
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(x) for x in doc]
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime.datetime):
        return doc.isoformat()
    return doc

def create_empty_cart(user_id):
    """
    Creates the default empty cart schema shape.
    """
    now = datetime.datetime.utcnow()
    return {
        "user_id": user_id,
        "items": [],
        "price_breakdown": {
            "subtotal": 0.0,
            "shipping": 0.0,
            "tax": 0.0,
            "discount": 0.0,
            "total": 0.0
        },
        "created_at": now,
        "updated_at": now
    }

def construct_cart_item(product_id, quantity, selected_attributes, custom_text, unit_price, snapshot):
    """
    Constructs a cart item document with normalized fields, line total, and snapshots.
    Generates a unique item_id (string UUID) to identify the line item.
    """
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")
    
    return {
        "item_id": str(uuid.uuid4()),
        "product_id": str(product_id),
        "quantity": int(quantity),
        "selected_attributes": selected_attributes or {},
        "custom_text": (custom_text or "").strip(),
        "unit_price": round(float(unit_price), 2),
        "line_total": round(float(unit_price * quantity), 2),
        "snapshot": snapshot or {}
    }

def are_items_duplicate(item1, item2):
    """
    Checks if two items match the duplicate item rule:
    same product_id AND same selected_attributes AND same custom_text.
    """
    # Compare product_id
    if str(item1.get("product_id")) != str(item2.get("product_id")):
        return False
    
    # Compare selected_attributes
    attrs1 = item1.get("selected_attributes") or {}
    attrs2 = item2.get("selected_attributes") or {}
    if attrs1 != attrs2:
        return False
    
    # Compare custom_text
    text1 = (item1.get("custom_text") or "").strip()
    text2 = (item2.get("custom_text") or "").strip()
    if text1 != text2:
        return False
    
    return True

def recalculate_cart_totals(cart):
    """
    Recalculates the cart's price_breakdown subtotal and total
    based on the sum of line_totals of its items.
    """
    subtotal = 0.0
    for item in cart.get("items", []):
        subtotal += item.get("line_total", 0.0)
        
    breakdown = cart.get("price_breakdown") or {}
    breakdown["subtotal"] = round(subtotal, 2)
    
    shipping = breakdown.get("shipping", 0.0)
    tax = breakdown.get("tax", 0.0)
    discount = breakdown.get("discount", 0.0)
    
    breakdown["total"] = round(subtotal + shipping + tax - discount, 2)
    cart["price_breakdown"] = breakdown
    cart["updated_at"] = datetime.datetime.utcnow()
    return cart
