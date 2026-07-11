VALID_TYPES = {"select", "color_swatch", "image_swatch", "toggle", "slider", "text_input", "number"}

VALID_ACCENT_COLORS = {"neon_pink", "neon_blue", "neon_violet", "neon_yellow"}

ACCENT_COLOR_MAP = {
    "neon_pink": "#FF2E8A",
    "neon_blue": "#18E7FF",
    "neon_violet": "#9B5CFF",
    "neon_yellow": "#FFD84D"
}

def validate_accent_color(value):
    if value not in VALID_ACCENT_COLORS:
        raise ValueError(f"Invalid accent_color '{value}'. Must be one of: {', '.join(sorted(VALID_ACCENT_COLORS))}")

def validate_attribute_schema(schema):
    if not isinstance(schema, list):
        raise ValueError("attribute_schema must be a list")

    seen_keys = set()
    for idx, attr in enumerate(schema):
        if not isinstance(attr, dict):
            raise ValueError(f"attribute_schema[{idx}]: each entry must be an object")

        key = attr.get("key")
        if not key:
            raise ValueError(f"attribute_schema[{idx}]: 'key' is required")
        if not isinstance(key, str):
            raise ValueError(f"attribute_schema[{idx}]: 'key' must be a string")
        if key in seen_keys:
            raise ValueError(f"attribute_schema[{idx}]: duplicate key '{key}'")
        seen_keys.add(key)

        label = attr.get("label")
        if not label:
            raise ValueError(f"attribute_schema[{idx}]: 'label' is required for key '{key}'")

        attr_type = attr.get("type")
        if not attr_type:
            raise ValueError(f"attribute_schema[{idx}]: 'type' is required for key '{key}'")
        if attr_type not in VALID_TYPES:
            raise ValueError(f"attribute_schema[{idx}]: invalid type '{attr_type}' for key '{key}'. Must be one of: {', '.join(sorted(VALID_TYPES))}")

        if attr_type in {"select", "color_swatch", "image_swatch"}:
            options = attr.get("options", [])
            if not isinstance(options, list):
                raise ValueError(f"attribute_schema[{idx}]: 'options' must be a list for key '{key}'")
            if len(options) < 2:
                raise ValueError(f"attribute_schema[{idx}]: '{attr_type}' type must have at least 2 options for key '{key}'")
            for oi, opt in enumerate(options):
                if not isinstance(opt, dict):
                    raise ValueError(f"attribute_schema[{idx}].options[{oi}]: each option must be an object")
                if "value" not in opt:
                    raise ValueError(f"attribute_schema[{idx}].options[{oi}]: 'value' is required for key '{key}'")
                if "label" not in opt:
                    raise ValueError(f"attribute_schema[{idx}].options[{oi}]: 'label' is required for key '{key}'")

        if attr_type == "toggle":
            options = attr.get("options", [])
            if not isinstance(options, list):
                raise ValueError(f"attribute_schema[{idx}]: 'options' must be a list for key '{key}'")
            if len(options) == 0:
                raise ValueError(f"attribute_schema[{idx}]: 'toggle' type must have at least 1 option for key '{key}'")
            for oi, opt in enumerate(options):
                if not isinstance(opt, dict):
                    raise ValueError(f"attribute_schema[{idx}].options[{oi}]: each option must be an object")
                if "value" not in opt:
                    raise ValueError(f"attribute_schema[{idx}].options[{oi}]: 'value' is required for key '{key}'")
                if "label" not in opt:
                    raise ValueError(f"attribute_schema[{idx}].options[{oi}]: 'label' is required for key '{key}'")
                if "price_delta" not in opt:
                    raise ValueError(f"attribute_schema[{idx}].options[{oi}]: 'price_delta' is required for toggle option '{opt.get('value', '')}' in key '{key}'")

        if attr_type in {"slider", "number"}:
            min_val = attr.get("min")
            max_val = attr.get("max")
            if min_val is not None and not isinstance(min_val, (int, float)):
                raise ValueError(f"attribute_schema[{idx}]: 'min' must be a number for key '{key}'")
            if max_val is not None and not isinstance(max_val, (int, float)):
                raise ValueError(f"attribute_schema[{idx}]: 'max' must be a number for key '{key}'")
            if min_val is not None and max_val is not None and min_val >= max_val:
                raise ValueError(f"attribute_schema[{idx}]: 'min' must be less than 'max' for key '{key}'")

        display_order = attr.get("display_order")
        if display_order is not None and not isinstance(display_order, (int, float)):
            raise ValueError(f"attribute_schema[{idx}]: 'display_order' must be a number for key '{key}'")

        affects_ai = attr.get("affects_ai_preview")
        if affects_ai is not None and not isinstance(affects_ai, bool):
            raise ValueError(f"attribute_schema[{idx}]: 'affects_ai_preview' must be a boolean for key '{key}'")

        required = attr.get("required")
        if required is not None and not isinstance(required, bool):
            raise ValueError(f"attribute_schema[{idx}]: 'required' must be a boolean for key '{key}'")
