import datetime
import random
from bson import ObjectId

VALID_ORDER_STATUSES = [
    "received", "reviewed", "quote_sent", "confirmed",
    "in_production", "ready", "out_for_delivery", "delivered", "cancelled"
]

def generate_order_number(db=None):
    """
    Generates a unique order number in the format GLX-YYYY-XXXXX.
    If a database object is provided, it tries to increment the sequence.
    Otherwise, it appends a random unique suffix.
    """
    year = datetime.datetime.utcnow().year
    prefix = f"GLX-{year}-"
    
    if db is not None:
        try:
            # Query the latest order number for this year
            latest_order = db.orders.find_one(
                {"order_number": {"$regex": f"^{prefix}"}},
                sort=[("created_at", -1)]
            )
            if latest_order:
                latest_num_str = latest_order["order_number"].replace(prefix, "")
                next_val = int(latest_num_str) + 1
                return f"{prefix}{next_val:05d}"
        except Exception:
            pass # fallback on exception
            
    # Random fallback (e.g. for testing or database-free context)
    rand_seq = random.randint(10000, 99999)
    return f"{prefix}{rand_seq}"

def construct_order(user_id, customer_snapshot, items, estimated_total):
    """
    Constructs an order document.
    """
    if not user_id or not customer_snapshot or not items:
        raise ValueError("User ID, customer snapshot, and items are required to place an order.")
        
    now = datetime.datetime.utcnow()
    
    # Check customer snapshot fields
    required_keys = ["name", "phone", "email", "address"]
    for key in required_keys:
        if not customer_snapshot.get(key):
            raise ValueError(f"Customer snapshot is missing required field: {key}")
            
    # Normalize items shape
    normalized_items = []
    for item in items:
        normalized_items.append({
            "product_id": str(item.get("product_id")),
            "product_title": str(item.get("product_title", "")),
            "category_name": str(item.get("category_name", "")),
            "selected_attributes": item.get("selected_attributes") or {},
            "quantity": int(item.get("quantity", 1)),
            "unit_price_estimate": round(float(item.get("unit_price_estimate", 0.0)), 2),
            "ai_preview_image": (item.get("ai_preview_image") or "").strip(),
            "reference_image": (item.get("reference_image") or "").strip()
        })

    return {
        "order_number": None, # Should be populated using generate_order_number
        "user_id": str(user_id),
        "customer_snapshot": {
            "name": customer_snapshot["name"].strip(),
            "phone": customer_snapshot["phone"].strip(),
            "email": customer_snapshot["email"].strip().lower(),
            "address": customer_snapshot["address"].strip()
        },
        "items": normalized_items,
        "estimated_total": round(float(estimated_total), 2),
        "final_quoted_price": None,
        "status": "received",
        "status_history": [
            {
                "status": "received",
                "note": "Order inquiry received and is awaiting review.",
                "updated_by": "system",
                "timestamp": now
            }
        ],
        "admin_notes": "",
        "customer_visible_note": "",
        "created_at": now,
        "updated_at": now
    }

def add_status_transition(order, next_status, note="", updated_by="admin"):
    """
    Appends a new status entry to the status_history and updates the primary status.
    """
    if next_status not in VALID_ORDER_STATUSES:
        raise ValueError(f"Invalid status: {next_status}. Must be one of {VALID_ORDER_STATUSES}")
        
    now = datetime.datetime.utcnow()
    
    order["status"] = next_status
    order["status_history"].append({
        "status": next_status,
        "note": (note or f"Order status changed to {next_status}.").strip(),
        "updated_by": updated_by,
        "timestamp": now
    })
    order["updated_at"] = now
    return order
