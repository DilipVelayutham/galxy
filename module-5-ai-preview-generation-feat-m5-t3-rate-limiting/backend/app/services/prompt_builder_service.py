import re

def sanitize_custom_text(text):
    """Sanitizes user input to prevent prompt injection and clean up the text."""
    if not text:
        return ""
        
    # Cast to string
    text = str(text)
    
    # 1. Limit length (avoid extremely long inputs that could overload the model or cost credits)
    text = text[:100]
    
    # 2. Check for common prompt injection keywords (case-insensitive)
    injection_patterns = [
        r"ignore\s+previous", r"ignore\s+instructions", r"override\s+prompt",
        r"system\s+prompt", r"forget\s+all", r"instead\s+of", r"you\s+must\s+generate",
        r"do\s+not\s+generate", r"change\s+prompt", r"act\s+as", r"delete\s+all"
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            # Prompt injection detected: neutralize input
            return "[Sanitized Text]"
            
    # 3. Strip any HTML tags
    text = re.sub(r"<[^>]*>", "", text)
    
    # 4. Filter down to safe characters: alphanumeric, spaces, quotes, hyphens, basic punctuation
    # Exclude wildcards, script tags, backslashes, etc.
    text = re.sub(r"[^\w\s\-\'\",\.!\?]", "", text)
    
    return text.strip()

def build_prompt(category, selected_attributes):
    """
    Assembles a prompt from the category's ai_prompt_template and selected_attributes.
    
    Resolves placeholders {key} with option labels, filters out non-preview attributes,
    sanitizes text inputs, and cleans up formatting.
    """
    template = category.get("ai_prompt_template", "")
    if not template:
        return ""
        
    schema_list = category.get("attribute_schema", [])
    
    # Create a fast lookup map for attributes
    schema_map = {attr["key"]: attr for attr in schema_list}
    
    resolved_values = {}
    
    # Identify all placeholders in the template (e.g. {font}, {color}, {custom_text})
    placeholders = re.findall(r"\{([^}]+)\}", template)
    
    for placeholder in placeholders:
        # Determine the key to query
        attr_key = placeholder
        
        # Check if attribute exists in category schema
        schema_attr = schema_map.get(attr_key)
        
        # If attribute has affects_ai_preview = False, we do not include it
        if schema_attr and not schema_attr.get("affects_ai_preview", True):
            resolved_values[placeholder] = ""
            continue
            
        # Get selected value from request payload
        val = selected_attributes.get(attr_key)
        
        if val is None or val == "":
            # Placeholder has no corresponding value (optional or missing)
            resolved_values[placeholder] = ""
            continue
            
        # Check if attribute is custom text
        is_text_input = schema_attr and schema_attr.get("type") in ["text_input", "text"]
        
        if attr_key == "custom_text" or is_text_input:
            # Sanitize text
            resolved_values[placeholder] = sanitize_custom_text(val)
        else:
            # Non-free-text options: resolve key to its corresponding label
            resolved_label = str(val)
            if schema_attr and "options" in schema_attr:
                for opt in schema_attr["options"]:
                    if str(opt.get("value")) == str(val):
                        resolved_label = opt.get("label", str(val))
                        break
            resolved_values[placeholder] = resolved_label

    # Format the template with resolved values
    try:
        final_prompt = template.format(**resolved_values)
    except KeyError as e:
        # Fallback if somehow a key was not resolved
        print(f"KeyError during formatting prompt: {e}")
        # Manual replace as fallback
        final_prompt = template
        for k, v in resolved_values.items():
            final_prompt = final_prompt.replace(f"{{{k}}}", str(v))
            
    # Clean up any leftover duplicate spaces or messy punctuation from empty replacements
    final_prompt = re.sub(r"\s+", " ", final_prompt)  # Collapse spaces
    final_prompt = re.sub(r"\s*,\s*", ", ", final_prompt)  # Clean commas
    final_prompt = re.sub(r"\s*\.\s*", ". ", final_prompt)  # Clean periods
    final_prompt = final_prompt.replace(" ,", ",").replace(" .", ".")
    
    return final_prompt.strip()
