from db import db
from models.cart import to_object_id

def validate_attributes(category_id, selected_attributes):
    """
    Validates selected_attributes against the category's attribute_schema.
    Raises ValueError with details if invalid, returns True if valid.
    """
    if selected_attributes is None:
        selected_attributes = {}
        
    if not isinstance(selected_attributes, dict):
        raise ValueError("selected_attributes must be a dictionary.")

    cat_id = to_object_id(category_id)
    category = db.categories.find_one({"_id": cat_id})
    if not category:
        raise ValueError(f"Category with ID {category_id} not found.")

    attribute_schema = category.get("attribute_schema", [])
    schema_keys = set()

    for attr in attribute_schema:
        key = attr.get("key")
        label = attr.get("label", key)
        attr_type = attr.get("type")
        required = attr.get("required", False)
        schema_keys.add(key)

        val = selected_attributes.get(key)

        # Check required fields
        if required:
            # None or empty string indicates missing required field
            if val is None or (isinstance(val, str) and not val.strip()):
                raise ValueError(f"Attribute '{label}' ({key}) is required.")

        # If value is present, validate its type and options
        if val is not None:
            if attr_type in ["select", "color_swatch", "image_swatch"]:
                options = attr.get("options", [])
                valid_options = [str(opt.get("value")) for opt in options]
                if str(val) not in valid_options:
                    raise ValueError(f"Invalid option '{val}' for attribute '{label}'. Allowed: {valid_options}")
                    
            elif attr_type == "toggle":
                if not isinstance(val, bool):
                    raise ValueError(f"Attribute '{label}' must be a boolean toggle (True/False).")
                    
            elif attr_type in ["slider", "number"]:
                try:
                    num_val = float(val)
                except (ValueError, TypeError):
                    raise ValueError(f"Attribute '{label}' must be a numeric value.")
                    
                min_limit = attr.get("min")
                max_limit = attr.get("max")
                
                if min_limit is not None and num_val < float(min_limit):
                    raise ValueError(f"Attribute '{label}' value {num_val} is below minimum allowed ({min_limit}).")
                if max_limit is not None and num_val > float(max_limit):
                    raise ValueError(f"Attribute '{label}' value {num_val} is above maximum allowed ({max_limit}).")
                    
            elif attr_type == "text_input":
                if not isinstance(val, str):
                    raise ValueError(f"Attribute '{label}' must be a text string.")

    # Check for unrecognized attributes
    submitted_keys = set(selected_attributes.keys())
    extra_keys = submitted_keys - schema_keys
    if extra_keys:
        raise ValueError(f"Unrecognized attributes submitted: {list(extra_keys)}")

    return True

def calculate_price(product_id, selected_attributes):
    """
    Calculates the unit price for a product based on its base_price
    plus the price_deltas of its selected attributes.
    """
    if selected_attributes is None:
        selected_attributes = {}
        
    prod_id = to_object_id(product_id)
    product = db.products.find_one({"_id": prod_id})
    if not product:
        raise ValueError(f"Product with ID {product_id} not found.")

    base_price = product.get("base_price", 0.0)
    surcharges = 0.0

    category_id = product.get("category_id")
    if category_id:
        category = db.categories.find_one({"_id": to_object_id(category_id)})
        if category:
            attribute_schema = category.get("attribute_schema", [])
            for attr in attribute_schema:
                key = attr.get("key")
                attr_type = attr.get("type")
                
                val = selected_attributes.get(key)
                if val is not None:
                    # Look up price delta from options
                    if attr_type in ["select", "color_swatch", "image_swatch"]:
                        options = attr.get("options", [])
                        for opt in options:
                            if str(opt.get("value")) == str(val):
                                surcharges += opt.get("price_delta", 0.0)
                                break
                                
    unit_price = base_price + surcharges
    return {
        "base_price": round(float(base_price), 2),
        "surcharges": round(float(surcharges), 2),
        "unit_price": round(float(unit_price), 2)
    }
