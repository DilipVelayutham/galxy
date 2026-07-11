from app.services.configurator_service import validate_attributes as real_validate
from app.services.pricing_service import calculate_price as real_calculate
from bson import ObjectId
from app.db import get_db

def validate_attributes(category_id, selected_attributes):
    """
    Validates selected_attributes against the category's real attribute_schema.
    Returns (is_valid, errors).
    """
    db = get_db()
    try:
        category = db.categories.find_one({"_id": ObjectId(category_id) if isinstance(category_id, str) else category_id})
    except Exception:
        category = None
    if not category:
        return False, {"category": "Category not found"}
        
    res = real_validate(category, selected_attributes)
    return res["valid"], res["errors"]

def calculate_price(product, selected_attributes):
    """
    Calculates the real dynamic price based on the product and category's active schema.
    Returns (unit_price_estimate, price_breakdown).
    """
    db = get_db()
    category_id = product.get("category_id")
    try:
        category = db.categories.find_one({"_id": ObjectId(category_id) if isinstance(category_id, str) else category_id})
    except Exception:
        category = None
        
    if not category:
        base_price = product.get("base_price", 0)
        return base_price, [{"name": "Base Price", "price": base_price}]
        
    res = real_calculate(product, category, selected_attributes, 1)
    
    # Map breakdown to match (name, price) structure
    breakdown = []
    for item in res["breakdown"]:
        breakdown.append({
            "name": item.get("label") or item.get("name"),
            "price": item.get("amount") or item.get("price")
        })
    return res["unit_price"], breakdown
