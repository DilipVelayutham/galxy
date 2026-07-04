<<<<<<< HEAD
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
=======
"""
prompt_builder_service.py — Module 5 AI Preview Generation (T2)
Responsible for assembling the final prompt string from a category's
ai_prompt_template (owned by Module 2) and the validated selected_attributes
(validated by Module 4).

This service NEVER defines prompt templates — it only fills them.
"""
import re
import logging

logger = logging.getLogger(__name__)

# ─── Injection-threat patterns to strip from customer free-text ──────────────────
_INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|prior)\s+(instructions?|prompts?|context)",
    r"(forget|disregard|override)\s+(your|all|the)\s+(instructions?|rules?|context)",
    r"you\s+are\s+now\s+a",
    r"act\s+as\s+(if\s+)?a",
    r"system\s*:",
    r"<\s*(script|img|iframe|object|embed)[^>]*>",  # basic HTML injection
]
_INJECTION_RE = re.compile(
    "|".join(_INJECTION_PATTERNS),
    re.IGNORECASE | re.DOTALL,
)
# Strip consecutive special characters (more than 3 of the same in a row)
_SPECIAL_CHARS_RE = re.compile(r"([^a-zA-Z0-9\s])\1{3,}")


def build_prompt(
    category: dict,
    selected_attributes: dict,
) -> str:
    """
    Fill the category's ai_prompt_template with values from selected_attributes.

    Rules (from spec §5):
    1. Placeholders map to attribute.key values; use the option **label** (not raw
       value) for human-readable text in the prompt.
    2. Attributes with affects_ai_preview == False are excluded entirely.
    3. free-text / custom_text fields are sanitized against prompt injection.
    4. Unset optional placeholders are replaced with '' and double-spaces cleaned up.
    5. Returns the final prompt string to be logged as prompt_used.

    Args:
        category: the full category document from Module 2 (must include
                  ai_prompt_template and attributes list).
        selected_attributes: dict keyed by attribute.key → selected value(s).

    Returns:
        Assembled prompt string ready to pass to ai_provider_client.
    """
    template: str = category.get("ai_prompt_template", "")
    if not template:
        raise ValueError(
            f"Category '{category.get('name', category.get('_id'))}' has no "
            "ai_prompt_template. Module 2 must define this before Module 5 can "
            "generate previews."
        )

    attributes: list[dict] = category.get("attributes", [])

    # Build a lookup: attribute_key → attribute_schema
    attr_schema_map: dict[str, dict] = {a["key"]: a for a in attributes}

    # Build a lookup: attribute_key → human-readable label for the selected value
    label_map: dict[str, str] = _resolve_labels(
        selected_attributes, attr_schema_map
    )

    # Replace all placeholders in the template
    filled = _fill_template(template, label_map)

    logger.debug("Built prompt: %s", filled)
    return filled


# ─── Private helpers ──────────────────────────────────────────────────────────────

def _resolve_labels(
    selected_attributes: dict,
    attr_schema_map: dict[str, dict],
) -> dict[str, str]:
    """
    For each selected attribute:
      - Skip attributes where affects_ai_preview == False (spec §5, rule 2).
      - For option-based attributes, resolve the selected value to its label.
      - For free-text attributes, sanitize the raw string (spec §5, rule 3).
    Returns a dict: {key: label_string}.
    """
    label_map: dict[str, str] = {}

    for key, raw_value in selected_attributes.items():
        schema = attr_schema_map.get(key)

        # Unknown attribute (not in category schema) — skip to be safe.
        if schema is None:
            logger.warning(
                "Attribute key '%s' not found in category schema; skipping.", key
            )
            continue

        # Spec §5, rule 2: skip attrs that don't affect the AI preview.
        if not schema.get("affects_ai_preview", True):
            continue

        # Determine the human-readable label for the selected value.
        attr_type = schema.get("type", "option")

        if attr_type in ("text", "text_input", "custom_text"):
            # Free-text field: sanitize before insertion (spec §5, rule 3).
            label_map[key] = _sanitize_text(str(raw_value))
        elif attr_type == "option" or "options" in schema:
            # Find the option whose value matches raw_value.
            options: list[dict] = schema.get("options", [])
            matched_label = _find_option_label(options, raw_value)
            if matched_label is not None:
                label_map[key] = matched_label
            else:
                # Fallback: use raw_value as-is (best effort).
                label_map[key] = str(raw_value)
        else:
            # Generic fallback.
            label_map[key] = str(raw_value)

    return label_map


def _find_option_label(options: list[dict], selected_value) -> str | None:
    """Return the label of the option whose value == selected_value, or None."""
    for opt in options:
        if str(opt.get("value", "")) == str(selected_value):
            return opt.get("label", str(selected_value))
    return None


def _sanitize_text(text: str) -> str:
    """
    Strip prompt injection attempts and excessive special characters.
    Returns a clean string safe to embed in an AI prompt.
    """
    # Remove injection patterns.
    cleaned = _INJECTION_RE.sub("", text)
    # Remove runs of special characters.
    cleaned = _SPECIAL_CHARS_RE.sub(r"\1", cleaned)
    # Collapse excessive whitespace.
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned


def _fill_template(template: str, label_map: dict[str, str]) -> str:
    """
    Replace {key} placeholders in template with resolved labels.
    Unresolved placeholders (optional attrs not selected) → empty string.
    Then clean up any resulting double spaces/punctuation artifacts.
    """
    # Find all placeholder keys in the template.
    placeholder_keys = re.findall(r"\{(\w+)\}", template)

    filled = template
    for key in placeholder_keys:
        value = label_map.get(key, "")  # empty string for unset optional attrs
        filled = filled.replace(f"{{{key}}}", value)

    # Clean up artefacts from empty substitutions:
    # e.g. "in  color" → "in color", "neon ,," → "neon"
    filled = re.sub(r",\s*,", ",", filled)        # double commas
    filled = re.sub(r",\s*\.", ".", filled)        # comma before period
    filled = re.sub(r"\s{2,}", " ", filled)        # multiple spaces
    filled = re.sub(r",\s*$", "", filled.strip())  # trailing comma

    return filled
>>>>>>> origin/main
