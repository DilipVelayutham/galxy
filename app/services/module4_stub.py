def validate_attributes(category, selected_attributes):
    # Mock validator for Module 4 integration
    if not category:
        return {"valid": False, "errors": {"category": "Category not found"}}
        
    category_attributes = category.get("attributes", [])
    valid_keys = {attr["key"] for attr in category_attributes}
    
    errors = {}
    for key in selected_attributes.keys():
        if key not in valid_keys:
            errors[key] = f"Attribute '{key}' is not defined in category schema."
            
    if errors:
        return {"valid": False, "errors": errors}
        
    return {"valid": True, "errors": {}}
