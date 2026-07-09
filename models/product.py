import datetime
from bson import ObjectId

def construct_product(category_id, title, slug, product_type, base_price, images=None, thumbnail="", description="", specifications=None, default_attributes=None, stock_status="in_stock", tags=None, is_featured=False, is_active=True):
    """
    Constructs a product document.
    """
    if not category_id or not title or not slug:
        raise ValueError("Category ID, title, and slug are required fields.")
        
    valid_types = ["pre_designed", "fully_custom"]
    if product_type not in valid_types:
        raise ValueError(f"Invalid product type: {product_type}. Must be one of {valid_types}.")
        
    valid_statuses = ["in_stock", "made_to_order", "out_of_stock"]
    if stock_status not in valid_statuses:
        raise ValueError(f"Invalid stock status: {stock_status}. Must be one of {valid_statuses}.")
        
    return {
        "category_id": ObjectId(str(category_id)) if category_id else None,
        "title": title.strip(),
        "slug": slug.strip().lower(),
        "type": product_type,
        "base_price": round(float(base_price), 2),
        "images": images or [],
        "thumbnail": (thumbnail or "").strip(),
        "description": (description or "").strip(),
        "specifications": specifications or {},
        "default_attributes": default_attributes or {},
        "stock_status": stock_status,
        "tags": tags or [],
        "is_featured": bool(is_featured),
        "is_active": bool(is_active),
        "views": 0,
        "rating_avg": 0.0,
        "rating_count": 0,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow()
    }
