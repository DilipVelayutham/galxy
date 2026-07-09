import re
from urllib.parse import urlparse

# Section 4: Variables & Constants You Must Define
SECTION_ENUM = ["hero", "about", "footer", "contact", "seo_home", "social_links"]

# Schemas detailing field type and whether they are required
SECTION_SCHEMAS = {
    "hero": {
        "headline": {"type": str, "required": True},
        "subheadline": {"type": str, "required": True},
        "background_video_url": {"type": str, "required": False, "nullable": True},
        "background_image_url": {"type": str, "required": True},
        "cta_text": {"type": str, "required": True},
        "cta_link": {"type": str, "required": True}
    },
    "about": {
        "title": {"type": str, "required": True},
        "body_text": {"type": str, "required": True, "max_length": 5000},
        "images": {"type": list, "required": True, "element_type": str},
        "founder_name": {"type": str, "required": True},
        "founder_photo": {"type": str, "required": False, "nullable": True}
    },
    "footer": {
        "tagline": {"type": str, "required": True},
        "quick_links": {"type": list, "required": True, "element_type": dict},
        "business_hours": {"type": str, "required": True}
    },
    "contact": {
        "phone": {"type": str, "required": True, "format": "phone"},
        "whatsapp_number": {"type": str, "required": True, "format": "phone"},
        "email": {"type": str, "required": True, "format": "email"},
        "address": {"type": str, "required": True},
        "map_embed_url": {"type": str, "required": False, "nullable": True}
    },
    "seo_home": {
        "meta_title": {"type": str, "required": True},
        "meta_description": {"type": str, "required": True},
        "og_image": {"type": str, "required": False, "nullable": True}
    },
    "social_links": {
        "instagram": {"type": str, "required": True},
        "facebook": {"type": str, "required": False, "nullable": True},
        "youtube": {"type": str, "required": False, "nullable": True}
    }
}

URL_FIELDS = {
    "hero": ["cta_link", "background_video_url", "background_image_url"],
    "about": ["images", "founder_photo"],
    "footer": ["quick_links[].url"],
    "contact": ["map_embed_url"],
    "seo_home": ["og_image"],
    "social_links": ["instagram", "facebook", "youtube"],
}

# Regex definitions for formats
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
# Allows standard phone numbers, international prefixes, spaces, hyphens, and parens
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,25}$")

def is_valid_absolute_url(url_string):
    """Helper to validate if a string is a valid absolute HTTP/HTTPS URL."""
    if not isinstance(url_string, str):
        return False
    # Quick visual and parse verification for absolute URLs
    if not (url_string.startswith("http://") or url_string.startswith("https://")):
        return False
    try:
        result = urlparse(url_string)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False

def is_valid_cta_link(url_string):
    """Helper to validate if a string is a valid HTTP/HTTPS URL or root-relative path."""
    if not isinstance(url_string, str):
        return False
    # Allow root-relative paths (e.g. /shop, /products/lighting)
    if url_string.startswith("/"):
        return True
    return is_valid_absolute_url(url_string)

# Keep alias for test backward-compatibility
is_valid_url = is_valid_cta_link

def validate_content(section, content):
    """
    Validates a content dictionary against the schema definition for the given section.
    
    Returns:
        (is_valid, errors) -> (bool, dict)
    """
    if section not in SECTION_ENUM:
        return False, {"section": f"Unknown section '{section}'. Must be one of {SECTION_ENUM}."}
    
    if not isinstance(content, dict):
        return False, {"content": "Content must be a JSON object (dictionary)."}
        
    schema = SECTION_SCHEMAS[section]
    errors = {}
    
    # 1. Check for unexpected fields (strict schema validation)
    for key in content.keys():
        if key not in schema:
            errors[key] = "Field is not allowed in this section."
            
    # 2. Check for required/nullable fields and type correctness
    for field_name, rule in schema.items():
        # Check if field is completely missing
        if field_name not in content:
            if rule.get("required"):
                errors[field_name] = "Field is required and cannot be null."
            continue
            
        # Check if field is explicitly set to null
        if content[field_name] is None:
            if not rule.get("nullable", False):
                errors[field_name] = "Field cannot be null."
            continue
            
        value = content[field_name]
        expected_type = rule["type"]
        
        if not isinstance(value, expected_type):
            errors[field_name] = f"Expected type {expected_type.__name__}, got {type(value).__name__}."
            continue
            
        # Specific element type checking for lists
        if expected_type is list:
            elem_type = rule.get("element_type")
            if elem_type:
                for idx, item in enumerate(value):
                    if not isinstance(item, elem_type):
                        errors[f"{field_name}[{idx}]"] = f"Expected type {elem_type.__name__}, got {type(item).__name__}."
                        
        # Specific string length limit checks
        if expected_type is str and "max_length" in rule:
            max_len = rule["max_length"]
            if len(value) > max_len:
                errors[field_name] = f"Maximum length exceeded. Limit is {max_len} characters."
                
        # Format checks for email/phone
        if expected_type is str and "format" in rule:
            fmt = rule["format"]
            if fmt == "email" and not EMAIL_REGEX.match(value):
                errors[field_name] = "Invalid email format."
            elif fmt == "phone" and not PHONE_REGEX.match(value):
                errors[field_name] = "Invalid phone number format."

    # 3. Validate URL fields based on URL_FIELDS constant
    url_targets = URL_FIELDS.get(section, [])
    for path in url_targets:
        # Simple path check: "quick_links[].url" vs direct field names
        if path == "quick_links[].url" and "quick_links" in content:
            links = content["quick_links"]
            if isinstance(links, list):
                for idx, link in enumerate(links):
                    if isinstance(link, dict):
                        # Ensure keys of quick_links are valid
                        # The shape of quick_links is: [ { "label", "url" } ]
                        # We also enforce that label and url are the only keys or at least required
                        for k in ["label", "url"]:
                            if k not in link:
                                errors[f"quick_links[{idx}].{k}"] = f"Field '{k}' is required inside quick_links element."
                        for k in link.keys():
                            if k not in ["label", "url"]:
                                errors[f"quick_links[{idx}].{k}"] = f"Field '{k}' is not allowed in quick_links element."
                        
                        # Validate the url field if it is present
                        if "url" in link:
                            url_val = link["url"]
                            if not isinstance(url_val, str):
                                errors[f"quick_links[{idx}].url"] = f"Expected type str, got {type(url_val).__name__}."
                            elif not is_valid_cta_link(url_val):
                                errors[f"quick_links[{idx}].url"] = "Invalid URL format."
        elif path == "images" and "images" in content:
            imgs = content["images"]
            if isinstance(imgs, list):
                for idx, img in enumerate(imgs):
                    if isinstance(img, str):
                        if not is_valid_absolute_url(img):
                             errors[f"images[{idx}]"] = "Invalid URL format."
        elif path in content and content[path] is not None:
            url_val = content[path]
            # Only cta_link is allowed to be root-relative
            checker = is_valid_cta_link if path == "cta_link" else is_valid_absolute_url
            if not checker(url_val):
                errors[path] = "Invalid URL format."

    return len(errors) == 0, errors
