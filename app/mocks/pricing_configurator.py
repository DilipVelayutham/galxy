from bson import ObjectId
from app.db import get_db

def validate_attributes(category_id, selected_attributes):
    """
    Validates selected_attributes against the category's attribute_schema.
    Returns (is_valid, error_message).
    """
    db = get_db()
    category = db.categories.find_one({"_id": ObjectId(category_id)})
    if not category:
        return False, {"category": "Category not found"}

    schema = category.get("attribute_schema", [])
    errors = {}
    
    # Check for required and valid attributes
    for attr in schema:
        key = attr.get("key")
        required = attr.get("required", False)
        
        if key not in selected_attributes or selected_attributes[key] is None or selected_attributes[key] == "":
            if required:
                errors[key] = f"Attribute '{attr.get('label', key)}' is required."
            continue
            
        val = selected_attributes[key]
        attr_type = attr.get("type")
        options = attr.get("options", [])
        
        # Validate options for select/swatches
        if attr_type in ["select", "color_swatch", "image_swatch"]:
            valid_values = [opt.get("value") for opt in options]
            if val not in valid_values:
                errors[key] = f"Invalid option '{val}' for '{attr.get('label', key)}'. Valid options: {valid_values}"
        
        # Validate numbers for sliders
        elif attr_type in ["slider", "number"]:
            try:
                num_val = float(val)
                min_val = attr.get("min")
                max_val = attr.get("max")
                if min_val is not None and num_val < float(min_val):
                    errors[key] = f"Value {val} is below minimum {min_val}."
                if max_val is not None and num_val > float(max_val):
                    errors[key] = f"Value {val} is above maximum {max_val}."
            except ValueError:
                errors[key] = f"Value '{val}' must be a number."
                
        # Validate text inputs
        elif attr_type == "text_input":
            if not isinstance(val, str):
                errors[key] = "Value must be a string."
                
    if errors:
        return False, errors
    return True, None

def calculate_price(product, selected_attributes):
    """
    Calculates the total price based on product base_price and attribute price_deltas.
    Returns (unit_price_estimate, price_breakdown).
    """
    db = get_db()
    base_price = product.get("base_price", 0)
    price_breakdown = [{"name": "Base Price", "price": base_price}]
    total = base_price
    
    category = db.categories.find_one({"_id": ObjectId(product.get("category_id"))})
    if not category:
        return total, price_breakdown
        
    schema = category.get("attribute_schema", [])
    
    for attr in schema:
        key = attr.get("key")
        if key in selected_attributes:
            val = selected_attributes[key]
            options = attr.get("options", [])
            for opt in options:
                if opt.get("value") == val:
                    delta = opt.get("price_delta", 0)
                    if delta != 0:
                        total += delta
                        price_breakdown.append({
                            "name": f"{attr.get('label', key)}: {opt.get('label', val)}",
                            "price": delta
                        })
                    break
                    
    return total, price_breakdown
