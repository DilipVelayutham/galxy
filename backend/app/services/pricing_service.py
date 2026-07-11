"""
GALXY E-Commerce Customization Platform
Pricing Service

This service acts as the ONLY source of truth for pricing calculations across the platform.
Handles base pricing, dynamic attribute pricing (selects, swatches, toggles, formula-based sliders),
and quantity scaling with comprehensive defensive checks.
"""

from typing import Any, Dict, List, Optional, Union
from app.utils.price_formula_helper import calculate_formula_price

def _parse_number(value: Any, default: Union[int, float] = 0) -> Union[int, float]:
    """
    Defensively parse a numeric value, preserving integer representation when appropriate.
    """
    if value is None:
        return default
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value
    try:
        f_val = float(value)
        return int(f_val) if f_val.is_integer() else f_val
    except (ValueError, TypeError):
        return default


def _get_attribute_definition(
    attribute_schema: Any,
    attribute_key: str
) -> Optional[Dict[str, Any]]:
    """
    Locate an attribute definition from the category attribute schema.
    """
    if isinstance(attribute_schema, dict):
        attr_def = attribute_schema.get(attribute_key)
        if isinstance(attr_def, dict):
            return attr_def

    if isinstance(attribute_schema, list):
        for attr in attribute_schema:
            if isinstance(attr, dict):
                key = (
                    attr.get("key")
                    or attr.get("id")
                    or attr.get("name")
                    or attr.get("attribute_key")
                )
                if str(key) == str(attribute_key):
                    return attr
    return None


def _find_matching_option(options: Any, selected_value: Any) -> Optional[Dict[str, Any]]:
    """
    Find a matching option dictionary from schema options.
    """
    val_to_match = selected_value
    if isinstance(selected_value, dict):
        val_to_match = (
            selected_value.get("value")
            or selected_value.get("id")
            or selected_value.get("key")
            or selected_value.get("label")
        )

    str_match = str(val_to_match).lower() if val_to_match is not None else ""

    if isinstance(options, list):
        for opt in options:
            if isinstance(opt, dict):
                opt_val = (
                    opt.get("value")
                    if opt.get("value") is not None
                    else (opt.get("id") if opt.get("id") is not None else opt.get("key"))
                )
                if opt_val is not None and str(opt_val).lower() == str_match:
                    return opt
                opt_label = opt.get("label") or opt.get("name")
                if opt_label is not None and str(opt_label).lower() == str_match:
                    return opt
            elif opt is not None and str(opt).lower() == str_match:
                return {"value": opt, "label": str(opt), "price_delta": 0}

    elif isinstance(options, dict):
        opt = options.get(val_to_match) or options.get(str(val_to_match))
        if isinstance(opt, dict):
            return opt

    return None


def calculate_price(
    product: Dict[str, Any],
    category: Dict[str, Any],
    selected_attributes: Dict[str, Any],
    quantity: int = 1
) -> Dict[str, Any]:
    """
    Calculate unit price, line total, and detailed pricing breakdown for a customized product.
    """
    if not isinstance(product, dict):
        product = {}
    if not isinstance(category, dict):
        category = {}
    if not isinstance(selected_attributes, dict):
        selected_attributes = {}

    try:
        qty = int(quantity) if quantity is not None else 1
        if qty < 1:
            qty = 1
    except (ValueError, TypeError):
        qty = 1

    base_price = _parse_number(product.get("base_price", 0), default=0)
    total: float = float(base_price)

    breakdown: List[Dict[str, Any]] = [
        {
            "key": "base_price",
            "label": "Base Price",
            "amount": base_price
        }
    ]

    schema = category.get("attribute_schema")
    if schema is None:
        schema = category.get("attributes", [])

    for attr_key, selected_val in selected_attributes.items():
        if selected_val is None:
            continue

        attr_def = _get_attribute_definition(schema, attr_key)
        if not attr_def:
            continue

        if attr_def.get("is_active") is False or str(attr_def.get("is_active")).lower() in ("false", "0"):
            continue

        attr_type = str(attr_def.get("type", "")).lower().strip()
        attr_label = str(attr_def.get("label") or attr_def.get("name") or attr_key)

        if not attr_type:
            if "options" in attr_def and attr_def["options"]:
                attr_type = "select"
            elif "price_formula" in attr_def and isinstance(attr_def["price_formula"], dict):
                attr_type = "slider"
            elif isinstance(selected_val, bool):
                attr_type = "toggle"

        # A) Option-based attributes: select, color_swatch, image_swatch
        if attr_type in ("select", "color_swatch", "image_swatch", "dropdown", "radio"):
            options = attr_def.get("options", [])
            matching_option = _find_matching_option(options, selected_val)
            if matching_option:
                price_delta = _parse_number(matching_option.get("price_delta", 0), default=0)
                total += float(price_delta)

                opt_label = str(
                    matching_option.get("label")
                    or matching_option.get("name")
                    or selected_val
                )
                breakdown.append({
                    "key": str(attr_key),
                    "label": f"{attr_label}: {opt_label}",
                    "amount": price_delta
                })

        # B) Boolean toggle attributes
        elif attr_type in ("toggle", "boolean", "checkbox"):
            is_active = False
            if isinstance(selected_val, bool):
                is_active = selected_val
            elif isinstance(selected_val, (int, float)):
                is_active = bool(selected_val)
            elif isinstance(selected_val, str):
                is_active = selected_val.lower().strip() in ("true", "1", "yes", "on")

            if is_active:
                price_delta = _parse_number(attr_def.get("price_delta", 0), default=0)
                total += float(price_delta)
                breakdown.append({
                    "key": str(attr_key),
                    "label": f"{attr_label}: Yes",
                    "amount": price_delta
                })

        # C) Numerical formula attributes: slider, number
        elif attr_type in ("slider", "number", "range"):
            formula = attr_def.get("price_formula")
            if not isinstance(formula, dict):
                if attr_def.get("base_included_units") is not None and attr_def.get("rate_per_unit") is not None:
                    formula = {
                        "base_included_units": attr_def.get("base_included_units"),
                        "rate_per_unit": attr_def.get("rate_per_unit"),
                        "unit": attr_def.get("unit") or attr_def.get("unit_label")
                    }
            if isinstance(formula, dict):
                base_included = formula.get("base_included_units", 0)
                rate = formula.get("rate_per_unit", 0)
                extra_units, extra_cost = calculate_formula_price(selected_val, base_included, rate)

                if extra_units > 0:
                    total += float(extra_cost)
                    unit_name = attr_def.get("unit") or attr_def.get("unit_label") or formula.get("unit") or formula.get("unit_label") or "units"
                    breakdown.append({
                        "key": str(attr_key),
                        "label": f"{attr_label}: +{extra_units} {unit_name}",
                        "amount": extra_cost
                    })

        # D) Text input attributes (or unknown types)
        elif attr_type in ("text_input", "text", "textarea"):
            continue

    unit_price = int(round(total))
    line_total = int(round(unit_price * qty))

    return {
        "unit_price": unit_price,
        "quantity": qty,
        "line_total": line_total,
        "breakdown": breakdown
    }

def calculate_custom_price(config: Dict[str, Any], settings: Dict[str, Any]) -> float:
    """
    Calculate customization price based on Sri settings for Next.js previewer:
    - Base price
    - Size: Add size_price_per_percent for each percent > 100%
    - Glow color: Extra cost associated with specific premium glow colors
    - Design text: Add text_price_per_char for each character
    - Floating height/intensity: Add float_price_per_level * float_intensity
    """
    base_price = settings.get("base_price", 99.0)
    size_price_per_percent = settings.get("size_price_per_percent", 1.0)
    color_prices = settings.get("color_prices", {})
    text_price_per_char = settings.get("text_price_per_char", 2.0)
    float_price_per_level = settings.get("float_price_per_level", 5.0)

    # 1. Base price
    total_price = base_price

    # 2. Size adjustment (+ cost for scale > 100%)
    size = float(config.get("size", 100))
    if size > 100:
        total_price += (size - 100) * size_price_per_percent

    # 3. Glow color price
    glow_color = config.get("glow_color", "").lower()
    color_extra = 0.0
    for key, value in color_prices.items():
        if key.lower() == glow_color:
            color_extra = float(value)
            break
    total_price += color_extra

    # 4. Custom design text length price
    design_text = config.get("design_text", "")
    total_price += len(design_text) * text_price_per_char

    # 5. Floating height/intensity level price
    float_intensity = float(config.get("float_intensity", 5))
    total_price += float_intensity * float_price_per_level

    return round(total_price, 2)

def calculate_price_by_id(product_id, category_id, selected_attributes, quantity=1):
    """
    Wrapper for order_service: resolves product and category and runs pricing calculation.
    """
    from bson import ObjectId
    from app.db import get_db
    
    db = get_db()
    try:
        product = db.products.find_one({"_id": ObjectId(product_id) if isinstance(product_id, str) else product_id})
        category = db.categories.find_one({"_id": ObjectId(category_id) if isinstance(category_id, str) else category_id})
    except Exception:
        product = None
        category = None
        
    if not product:
        # Fallback to empty product
        product = {"base_price": 100.0}
        
    if not category:
        # Return fallback pricing
        unit_price = float(product.get("base_price", 100.0))
        return {
            "unit_price": unit_price,
            "line_total": unit_price * quantity,
            "breakdown": [{"label": "Base Price", "amount": unit_price}]
        }
        
    return calculate_price(product, category, selected_attributes, quantity)

