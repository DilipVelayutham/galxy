import re

def sanitize_custom_text(text):
    if not text:
        return ""
    
    # Cap length at 100 characters to prevent excessive tokens/abuse
    text = str(text)[:100]
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # List of common prompt injection keywords (case-insensitive)
    injection_patterns = [
        r"ignore\s+(?:all\s+)?previous\s+instructions",
        r"ignore\s+(?:all\s+)?prior\s+instructions",
        r"instead\s+of\s+generating",
        r"system\s+prompt",
        r"you\s+must\s+instead",
        r"forget\s+(?:what\s+I\s+said|everything)",
        r"dan\s+mode",
        r"system\s+override"
    ]
    
    sanitized = text
    for pattern in injection_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
    
    # Clean up characters that might interfere with prompts or templates
    sanitized = re.sub(r'[\{\}\[\]\<\>]', '', sanitized)
    
    # Replace multiple spaces with a single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    return sanitized.strip()

def build_prompt(category, selected_attributes):
    if not category:
        return ""
    
    template = category.get("ai_prompt_template", "")
    if not template:
        return ""
        
    attributes = category.get("attributes", [])
    attr_map = {attr["key"]: attr for attr in attributes}
    
    # Find all placeholders in the template: {key}
    placeholders = re.findall(r'\{([a-zA-Z0-9_]+)\}', template)
    
    replacements = {}
    for key in placeholders:
        if key == "category_name":
            replacements[key] = category.get("name", "")
            continue
            
        attr = attr_map.get(key)
        if not attr:
            # Key not found in category attributes schema - replace with empty string
            replacements[key] = ""
            continue
            
        # Visibility filtering: If effects are set to False, drop it entirely
        if not attr.get("affects_ai_preview", True):
            replacements[key] = ""
            continue
            
        val = selected_attributes.get(key)
        if val is None or val == "":
            replacements[key] = ""
            continue
            
        # Determine if text type or options list
        if attr.get("type") == "text" or "options" not in attr or not attr["options"]:
            if key == "custom_text" or attr.get("type") == "text":
                replacements[key] = sanitize_custom_text(val)
            else:
                replacements[key] = str(val)
        else:
            # Map selected option value/code to option text label
            options = attr.get("options", [])
            option_label = ""
            for opt in options:
                if isinstance(opt, dict):
                    opt_code = opt.get("code") or opt.get("value")
                    if str(opt_code) == str(val):
                        option_label = opt.get("label", "")
                        break
                elif str(opt) == str(val):
                    option_label = str(opt)
                    break
            
            replacements[key] = option_label
            
    # Do replacements
    prompt = template
    for key, replacement in replacements.items():
        prompt = prompt.replace(f"{{{key}}}", replacement)
        
    # Clean up formatting: double spaces, dangling punctuation, empty params
    prompt = re.sub(r'\s+', ' ', prompt)
    prompt = re.sub(r'\s*,\s*,', ',', prompt)
    prompt = re.sub(r'\s*,\s*\.', '.', prompt)
    prompt = re.sub(r'\s*\.\s*\.', '.', prompt)
    
    prompt = prompt.strip()
    prompt = re.sub(r'^[\s,]+', '', prompt)
    prompt = re.sub(r'[\s,]+$', '', prompt)
    
    return prompt
