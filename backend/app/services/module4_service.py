from bson import ObjectId
from app.database import categories

def validate_attributes(category_id, selected_attributes):
    """
    Validates selected_attributes against the category's attribute_schema.
    Simulates Module 4's validation engine.
    
    Returns:
        dict: { "valid": bool, "errors": list of str }
    """
    errors = []
    
    try:
        # Resolve category_id (handle string or ObjectId)
        query_id = category_id
        if isinstance(category_id, str):
            try:
                query_id = ObjectId(category_id)
            except Exception:
                pass  # Use string if not ObjectId
                
        category = categories.find_one({"$or": [{"_id": query_id}, {"category_id": category_id}]})
        
        if not category:
            return {
                "valid": False,
                "errors": [f"Category '{category_id}' not found."]
            }
            
        schema_list = category.get("attribute_schema", [])
        
        for attr in schema_list:
            key = attr.get("key")
            label = attr.get("label", key)
            required = attr.get("required", False)
            
            # Check presence of required attribute
            val = selected_attributes.get(key)
            if required and (val is None or str(val).strip() == ""):
                errors.append(f"Attribute '{label}' ({key}) is required.")
                continue
                
            # If the attribute has value, validate its type/options
            if val is not None and str(val).strip() != "":
                attr_type = attr.get("type", "select")
                options = attr.get("options", [])
                
                # Check select/swatch options validation
                if attr_type in ["select", "color_swatch", "image_swatch"] and options:
                    valid_values = [str(opt.get("value")) for opt in options]
                    if str(val) not in valid_values:
                        errors.append(f"Invalid option '{val}' for attribute '{label}'. Valid options are: {valid_values}")
                        
                # Check numeric range limits for slider/number
                elif attr_type in ["slider", "number"]:
                    try:
                        num_val = float(val)
                        min_val = attr.get("min")
                        max_val = attr.get("max")
                        
                        if min_val is not None and num_val < float(min_val):
                            errors.append(f"Attribute '{label}' must be at least {min_val}.")
                        if max_val is not None and num_val > float(max_val):
                            errors.append(f"Attribute '{label}' must be at most {max_val}.")
                    except ValueError:
                        errors.append(f"Attribute '{label}' must be a valid number.")
                        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
        
    except Exception as e:
        print(f"[Validation Engine] Error running validation: {e}")
        return {
            "valid": False,
            "errors": [f"Internal validation error: {str(e)}"]
        }
