import logging
from bson import ObjectId
from app.database import db_conn

logger = logging.getLogger(__name__)

def validate_product_data(data, is_update=False, product_id=None):
    """
    Validates product data for creation or updates.
    Returns:
        tuple: (errors, warning_message, validated_data)
        - errors (dict): Keyed by field name, containing validation error details. Empty if valid.
        - warning_message (str): Warning text for soft validation rules (e.g. activating without images).
        - validated_data (dict): Cleaned and cast data values ready to write to DB.
    """
    errors = {}
    warning_message = ""
    validated_data = {}

    db = db_conn.db

    # 1. Title Validation
    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            errors["title"] = "Title must be a non-empty string."
        elif len(title.strip()) < 3 or len(title.strip()) > 120:
            errors["title"] = "Title must be between 3 and 120 characters."
        else:
            validated_data["title"] = title.strip()
    elif not is_update:
        errors["title"] = "Title is required."

    # 2. Base Price Validation
    if "base_price" in data:
        try:
            base_price = float(data["base_price"])
            if base_price <= 0:
                errors["base_price"] = "Base price must be a positive number."
            else:
                validated_data["base_price"] = base_price
        except (ValueError, TypeError):
            errors["base_price"] = "Base price must be a valid number."
    elif not is_update:
        errors["base_price"] = "Base price is required."

    # 3. Type Validation
    if "type" in data:
        p_type = data["type"]
        if p_type not in ["pre_designed", "fully_custom"]:
            errors["type"] = "Type must be 'pre_designed' or 'fully_custom'."
        else:
            validated_data["type"] = p_type
    elif not is_update:
        errors["type"] = "Type is required."

    # 4. Stock Status Validation
    if "stock_status" in data:
        status = data["stock_status"]
        if status not in ["in_stock", "made_to_order", "out_of_stock"]:
            errors["stock_status"] = "Stock status must be one of: 'in_stock', 'made_to_order', 'out_of_stock'."
        else:
            validated_data["stock_status"] = status
    elif not is_update:
        errors["stock_status"] = "Stock status is required."

    # 5. Category ID Validation (disallowed on update)
    category = None
    if "category_id" in data:
        if is_update:
            errors["category_id"] = "Changing category_id after creation is disallowed."
        else:
            cat_id_str = data["category_id"]
            if not cat_id_str:
                errors["category_id"] = "Category ID is required."
            else:
                try:
                    cat_id = ObjectId(cat_id_str)
                    if db is not None:
                        # Category must exist and be active
                        category = db.categories.find_one({"_id": cat_id, "is_active": True})
                        if not category:
                            errors["category_id"] = "Category does not exist or is inactive."
                        else:
                            validated_data["category_id"] = cat_id
                            validated_data["category_slug"] = category.get("slug")
                    else:
                        # Offline fallback for testing
                        validated_data["category_id"] = cat_id
                        validated_data["category_slug"] = "mock-category-slug"
                except Exception:
                    errors["category_id"] = "Invalid Category ID format."
    elif not is_update:
        errors["category_id"] = "Category ID is required."

    # 6. Default Attributes Validation
    if "default_attributes" in data:
        default_attrs = data["default_attributes"]
        if not isinstance(default_attrs, dict):
            errors["default_attributes"] = "Default attributes must be a dictionary."
        else:
            validated_data["default_attributes"] = default_attrs
            
            # Fetch Category Schema to validate
            if not category and is_update and product_id and db is not None:
                try:
                    prod = db.products.find_one({"_id": ObjectId(product_id)})
                    if prod and "category_id" in prod:
                        category = db.categories.find_one({"_id": prod["category_id"]})
                except Exception as e:
                    logger.error(f"Error fetching product category for validation: {e}")
            
            if category:
                schema_list = category.get("attribute_schema", [])
                schema_by_key = {s["key"]: s for s in schema_list if "key" in s}
                attr_errors = {}
                
                for key, val in default_attrs.items():
                    if key not in schema_by_key:
                        attr_errors[key] = f"Attribute '{key}' is not defined in category attribute_schema."
                        continue
                    
                    schema = schema_by_key[key]
                    s_type = schema.get("type")
                    
                    # Validate select, color_swatch, and image_swatch options
                    if s_type in ["select", "color_swatch", "image_swatch"]:
                        options = schema.get("options", [])
                        valid_values = [opt.get("value") for opt in options if "value" in opt]
                        if val not in valid_values:
                            attr_errors[key] = f"Value '{val}' is invalid. Allowed options are: {valid_values}."
                            
                    # Validate toggles
                    elif s_type == "toggle":
                        if not isinstance(val, bool) and str(val).lower() not in ["true", "false"]:
                            attr_errors[key] = "Value must be a boolean."
                            
                    # Validate slider or numeric limits
                    elif s_type in ["slider", "number"]:
                        try:
                            num_val = float(val)
                            min_val = schema.get("min")
                            max_val = schema.get("max")
                            if min_val is not None and num_val < float(min_val):
                                attr_errors[key] = f"Value {num_val} is less than minimum {min_val}."
                            if max_val is not None and num_val > float(max_val):
                                attr_errors[key] = f"Value {num_val} exceeds maximum {max_val}."
                        except (ValueError, TypeError):
                            attr_errors[key] = "Value must be a valid number."
                            
                if attr_errors:
                    errors["default_attributes"] = attr_errors

    # 7. Other Optional Fields
    if "description" in data:
        validated_data["description"] = str(data["description"]).strip()

    if "specifications" in data:
        specs = data["specifications"]
        if not isinstance(specs, dict):
            errors["specifications"] = "Specifications must be a dictionary."
        else:
            validated_data["specifications"] = specs

    if "tags" in data:
        tags = data["tags"]
        if not isinstance(tags, list):
            errors["tags"] = "Tags must be a list of strings."
        else:
            validated_data["tags"] = [str(t).strip() for t in tags]

    if "is_featured" in data:
        validated_data["is_featured"] = bool(data["is_featured"])

    if "is_active" in data:
        is_active = bool(data["is_active"])
        validated_data["is_active"] = is_active
        
        # Soft Check: At least one image required before product can be active
        if is_active:
            existing_images = []
            if is_update and product_id and db is not None:
                try:
                    prod = db.products.find_one({"_id": ObjectId(product_id)})
                    if prod:
                        existing_images = prod.get("images", [])
                except Exception:
                    pass
            # If images are provided in the payload, override existing
            if "images" in data:
                existing_images = data["images"]
                
            if not existing_images:
                warning_message = "Admin Warning: Product contains zero images. It is recommended to upload at least one image before setting is_active to true."

    return errors, warning_message, validated_data
