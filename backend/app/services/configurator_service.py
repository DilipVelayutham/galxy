"""
GALXY E-Commerce Customization Platform
Configurator Service

Handles server-side validation of customer-selected attributes against category schemas.
Ensures zero arbitrary data injection, validates required fields, enforces option membership,
boolean types, numerical slider bounds, and text input lengths.
"""

from typing import Any, Dict, List

def validate_attributes(category: Dict[str, Any], selected_attributes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate customer-selected attributes against the category schema.

    Args:
        category (Dict[str, Any]): Category document containing 'attribute_schema'.
        selected_attributes (Dict[str, Any]): Dictionary of customer selections.

    Returns:
        Dict[str, Any]: Exact contract structure:
            {
                "valid": bool,
                "errors": Dict[str, str]
            }
    """
    if not isinstance(category, dict):
        category = {}
    if not isinstance(selected_attributes, dict):
        selected_attributes = {}

    attribute_schema = category.get("attribute_schema")
    if attribute_schema is None:
        attribute_schema = category.get("attributes", [])
    if not isinstance(attribute_schema, list):
        attribute_schema = []

    errors: Dict[str, str] = {}

    # Build schema map of keys to identify details quickly
    schema_map: Dict[str, dict] = {}
    for attr in attribute_schema:
        if isinstance(attr, dict):
            key = attr.get("key") or attr.get("id") or attr.get("name") or attr.get("attribute_key")
            if key is not None:
                schema_map[str(key)] = attr

    # 1. Validate provided selected attributes
    for key, val in selected_attributes.items():
        # Rule 1: Unknown keys
        if key not in schema_map:
            errors[key] = "Unknown attribute"
            continue

        attr = schema_map[key]

        # Rule 10: Disabled Attributes
        if attr.get("is_active") is False or str(attr.get("is_active")).lower() in ("false", "0"):
            errors[key] = "Attribute is disabled."
            continue

        attr_type = str(attr.get("type", "")).lower().strip()

        # For toggle types, None is invalid (must be boolean), so don't skip
        # For other types, ignore null/empty values — required check handles them below
        if attr_type not in ("toggle", "boolean", "checkbox"):
            if val is None or val == "":
                continue

        # Rule 3, 4, 5: Select, Color Swatch, Image Swatch
        if attr_type in ("select", "color_swatch", "image_swatch", "dropdown", "radio"):
            options = attr.get("options", [])
            if not isinstance(options, list):
                options = []
            
            allowed_values = []
            for opt in options:
                if isinstance(opt, dict):
                    opt_val = opt.get("value") if opt.get("value") is not None else (opt.get("id") if opt.get("id") is not None else opt.get("key"))
                    if opt_val is not None:
                        allowed_values.append(opt_val)
                    opt_lbl = opt.get("label") or opt.get("name")
                    if opt_lbl is not None:
                        allowed_values.append(opt_lbl)
                elif opt is not None:
                    allowed_values.append(opt)

            # Convert to string for broad checking, case-insensitive
            allowed_values_str = [str(v).lower() for v in allowed_values]
            if str(val).lower() not in allowed_values_str:
                errors[key] = "Invalid option selected."

        # Rule 6: Toggle
        elif attr_type in ("toggle", "boolean", "checkbox"):
            if not isinstance(val, bool):
                errors[key] = "Invalid value. Must be a boolean."

        # Rule 7, 8: Slider, Number
        elif attr_type in ("slider", "number", "range"):
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                errors[key] = "Value must be numeric."
            else:
                min_val = attr.get("min")
                max_val = attr.get("max")
                
                is_min_numeric = isinstance(min_val, (int, float)) and not isinstance(min_val, bool)
                is_max_numeric = isinstance(max_val, (int, float)) and not isinstance(max_val, bool)

                if is_min_numeric and is_max_numeric:
                    if not (min_val <= val <= max_val):
                        errors[key] = f"Value must be between {min_val} and {max_val}"
                elif is_min_numeric:
                    if val < min_val:
                        errors[key] = f"Value must be at least {min_val}"
                elif is_max_numeric:
                    if val > max_val:
                        errors[key] = f"Value must be at most {max_val}"

        # Rule 9: Text Input
        elif attr_type in ("text_input", "text", "textarea"):
            if not isinstance(val, str):
                errors[key] = "Value must be a string."
            else:
                max_len = attr.get("max_length") or attr.get("max")
                if max_len is None:
                    max_len = 60
                try:
                    max_len = int(max_len)
                except (ValueError, TypeError):
                    max_len = 60
                if len(val) > max_len:
                    errors[key] = "Maximum length exceeded."

    # 2. Rule 2: Required Fields validation
    for key, attr in schema_map.items():
        is_active = attr.get("is_active", True)
        if is_active is not False and str(is_active).lower() not in ("false", "0"):
            if attr.get("required") is True or str(attr.get("required")).lower() in ("true", "1"):
                if key not in selected_attributes or selected_attributes[key] is None or selected_attributes[key] == "":
                    errors[key] = "This field is required."

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
