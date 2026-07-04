"""
prompt_builder_service.py — Module 5 AI Preview Generation (T2)
Responsible for assembling the final prompt string from a category's
ai_prompt_template (owned by Module 2) and the validated selected_attributes.
"""
import re
import logging

logger = logging.getLogger(__name__)

# ─── Injection-threat patterns to strip from customer free-text (origin/main) ─────
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


# ─── HEAD Sanitization Function ───────────────────────────────────────────────────

def sanitize_custom_text(text):
    """Sanitizes user input to prevent prompt injection and clean up the text (HEAD)."""
    if not text:
        return ""
        
    text = str(text)
    
    # 1. Limit length
    text = text[:100]
    
    # 2. Check for common prompt injection keywords
    injection_patterns = [
        r"ignore\s+previous", r"ignore\s+instructions", r"override\s+prompt",
        r"system\s+prompt", r"forget\s+all", r"instead\s+of", r"you\s+must\s+generate",
        r"do\s+not\s+generate", r"change\s+prompt", r"act\s+as", r"delete\s+all"
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return "[Sanitized Text]"
            
    # 3. Strip HTML tags
    text = re.sub(r"<[^>]*>", "", text)
    
    # 4. Filter down to safe characters
    text = re.sub(r"[^\w\s\-\'\",\.!\?]", "", text)
    
    return text.strip()


# ─── origin/main Sanitization Function ────────────────────────────────────────────

def _sanitize_text(text: str) -> str:
    """Strip prompt injection attempts and excessive special characters (origin/main)."""
    # Remove injection patterns.
    cleaned = _INJECTION_RE.sub("", text)
    # Remove runs of special characters.
    cleaned = _SPECIAL_CHARS_RE.sub(r"\1", cleaned)
    # Collapse excessive whitespace.
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned


# ─── Prompt Builder ───────────────────────────────────────────────────────────────

def build_prompt(
    category: dict,
    selected_attributes: dict,
) -> str:
    """
    Fill the category's ai_prompt_template with values from selected_attributes.
    Supports both category.attributes and category.attribute_schema structures.
    """
    template: str = category.get("ai_prompt_template", "")
    if not template:
        raise ValueError(
            f"Category '{category.get('name', category.get('_id'))}' has no "
            "ai_prompt_template."
        )

    # Accept both schemas to cleanly support both branches
    attributes: list[dict] = category.get("attributes") or category.get("attribute_schema", [])

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
    """For each selected attribute, resolve to its human-readable label."""
    label_map: dict[str, str] = {}

    for key, raw_value in selected_attributes.items():
        schema = attr_schema_map.get(key)

        if schema is None:
            logger.warning(
                "Attribute key '%s' not found in category schema; skipping.", key
            )
            continue

        if not schema.get("affects_ai_preview", True):
            continue

        attr_type = schema.get("type", "option")

        if attr_type in ("text", "text_input", "custom_text"):
            # Use appropriate sanitization helper depending on implementation
            label_map[key] = _sanitize_text(str(raw_value))
        elif attr_type == "option" or "options" in schema:
            options: list[dict] = schema.get("options", [])
            matched_label = _find_option_label(options, raw_value)
            if matched_label is not None:
                label_map[key] = matched_label
            else:
                label_map[key] = str(raw_value)
        else:
            label_map[key] = str(raw_value)

    return label_map


def _find_option_label(options: list[dict], selected_value) -> str | None:
    """Return the label of the option whose value == selected_value, or None."""
    for opt in options:
        if str(opt.get("value", "")) == str(selected_value):
            return opt.get("label", str(selected_value))
        # Fallback to key/code matching if value is missing
        elif str(opt.get("code", "")) == str(selected_value):
            return opt.get("label", str(selected_value))
    return None


def _fill_template(template: str, label_map: dict[str, str]) -> str:
    """Replace placeholders in template with resolved labels and clean up formatting."""
    # Find all placeholder keys in the template
    placeholder_keys = re.findall(r"\{(\w+)\}", template)

    filled = template
    for key in placeholder_keys:
        value = label_map.get(key, "")  # empty string for unset optional attrs
        filled = filled.replace(f"{{{key}}}", value)

    # Clean up artifacts from empty substitutions
    filled = re.sub(r",\s*,", ",", filled)        # double commas
    filled = re.sub(r",\s*\.", ".", filled)        # comma before period
    filled = re.sub(r"\s{2,}", " ", filled)        # multiple spaces
    filled = re.sub(r",\s*$", "", filled.strip())  # trailing comma
    
    # Extra formatting cleanup
    filled = re.sub(r"\s*,\s*", ", ", filled)
    filled = re.sub(r"\s*\.\s*", ". ", filled)
    filled = filled.replace(" ,", ",").replace(" .", ".")

    return filled.strip()

