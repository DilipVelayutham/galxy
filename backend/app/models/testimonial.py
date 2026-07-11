from datetime import datetime
from bson import ObjectId

def validate_testimonial(data, is_update=False):
    """
    Validates testimonial data against constraints.
    Returns a dictionary of clean data or raises ValueError.
    """
    errors = []
    
    # Required fields on creation
    if not is_update:
        if "customer_name" not in data or not data["customer_name"] or not str(data["customer_name"]).strip():
            errors.append("customer_name is required")
        if "quote" not in data or not data["quote"] or not str(data["quote"]).strip():
            errors.append("quote is required")
            
    # Field type/format checks if they are in data
    if "customer_name" in data:
        name = str(data["customer_name"]).strip()
        if not name and not is_update:
            errors.append("customer_name cannot be empty")
            
    if "customer_location" in data:
        loc = data["customer_location"]
        if loc is not None and not isinstance(loc, str):
            errors.append("customer_location must be a string or null")
            
    if "quote" in data:
        quote = str(data["quote"]).strip()
        if not quote and not is_update:
            errors.append("quote cannot be empty")
            
    if "rating" in data:
        try:
            rating = int(data["rating"])
            if rating < 1 or rating > 5:
                errors.append("rating must be between 1 and 5")
        except (ValueError, TypeError):
            errors.append("rating must be an integer")
            
    if "image" in data:
        img = data["image"]
        if img is not None and not isinstance(img, str):
            errors.append("image must be a string (URL) or null")
            
    if "display_order" in data:
        try:
            display_order = int(data["display_order"])
            if display_order < 1:
                errors.append("display_order must be a positive integer")
        except (ValueError, TypeError):
            errors.append("display_order must be an integer")

    if "source" in data:
        source = data["source"]
        if source not in ["review", "manual"]:
            errors.append("source must be 'review' or 'manual'")

    if "review_id" in data:
        review_id = data["review_id"]
        if review_id is not None and review_id != "":
            try:
                ObjectId(str(review_id))
            except Exception:
                errors.append("review_id must be a valid ObjectId string or null")

    if "is_active" in data:
        is_active = data["is_active"]
        if not isinstance(is_active, bool):
            errors.append("is_active must be a boolean")

    if errors:
        raise ValueError("; ".join(errors))

    # Construct cleaned data dict
    clean_data = {}
    
    if "customer_name" in data:
        clean_data["customer_name"] = str(data["customer_name"]).strip()
    if "customer_location" in data:
        loc = data["customer_location"]
        clean_data["customer_location"] = str(loc).strip() if loc else ""
    if "quote" in data:
        clean_data["quote"] = str(data["quote"]).strip()
    if "rating" in data:
        clean_data["rating"] = int(data["rating"])
    elif not is_update:
        clean_data["rating"] = 5

    if "image" in data:
        img = data["image"]
        clean_data["image"] = str(img).strip() if img else None
    elif not is_update:
        clean_data["image"] = None

    if "display_order" in data:
        clean_data["display_order"] = int(data["display_order"])
    elif not is_update:
        clean_data["display_order"] = 1

    if "is_active" in data:
        clean_data["is_active"] = bool(data["is_active"])
    elif not is_update:
        clean_data["is_active"] = True

    if "source" in data:
        clean_data["source"] = data["source"]
    elif not is_update:
        clean_data["source"] = "manual"

    if "review_id" in data:
        review_id = data["review_id"]
        if review_id and review_id != "":
            clean_data["review_id"] = ObjectId(str(review_id))
        else:
            clean_data["review_id"] = None
    elif not is_update:
        clean_data["review_id"] = None

    if not is_update:
        clean_data["created_at"] = datetime.utcnow()

    return clean_data
