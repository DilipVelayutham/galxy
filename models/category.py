import datetime

def construct_category(slug, name, description, cover_image="", banner_image="", display_order=0, is_active=True, ai_prompt_template=""):
    """
    Constructs a category document.
    """
    if not slug or not name:
        raise ValueError("Category slug and name are required fields.")
        
    return {
        "slug": slug.strip().lower(),
        "name": name.strip(),
        "description": (description or "").strip(),
        "cover_image": cover_image,
        "banner_image": banner_image,
        "display_order": int(display_order),
        "is_active": bool(is_active),
        "attribute_schema": [],
        "ai_prompt_template": ai_prompt_template or "",
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow()
    }

def construct_attribute_option(value, label, price_delta=0.0, preview_image=""):
    """
    Constructs an option entry for an attribute.
    """
    if value is None or not label:
        raise ValueError("Option value and label are required.")
        
    return {
        "value": str(value).strip(),
        "label": label.strip(),
        "price_delta": round(float(price_delta), 2),
        "preview_image": (preview_image or "").strip()
    }

def construct_attribute(key, label, type_name, options=None, min_val=None, max_val=None, step=None, affects_ai_preview=True, required=True, display_order=1):
    """
    Constructs an attribute schema to be embedded inside category's attribute_schema list.
    """
    valid_types = ["select", "color_swatch", "image_swatch", "toggle", "slider", "text_input", "number"]
    if type_name not in valid_types:
        raise ValueError(f"Invalid attribute type: {type_name}. Must be one of {valid_types}.")
        
    if not key or not label:
        raise ValueError("Attribute key and label are required.")
        
    return {
        "key": key.strip(),
        "label": label.strip(),
        "type": type_name,
        "options": options or [],
        "min": float(min_val) if min_val is not None else None,
        "max": float(max_val) if max_val is not None else None,
        "step": float(step) if step is not None else None,
        "affects_ai_preview": bool(affects_ai_preview),
        "required": bool(required),
        "display_order": int(display_order)
    }
