import os
import sys
import pytest

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.configurator_service import validate_attributes


@pytest.fixture
def sample_category() -> dict:
    """Fixture containing a comprehensive attribute schema for validation testing."""
    return {
        "attribute_schema": [
            {
                "key": "font",
                "label": "Font Style",
                "type": "select",
                "required": True,
                "is_active": True,
                "options": [
                    {"value": "cursive", "label": "Cursive", "price_delta": 0},
                    {"value": "bold", "label": "Bold", "price_delta": 150},
                ],
            },
            {
                "key": "primary_color",
                "label": "Primary Color",
                "type": "color_swatch",
                "required": False,
                "is_active": True,
                "options": [
                    {"value": "red", "label": "Red", "price_delta": 0},
                    {"value": "blue", "label": "Blue", "price_delta": 50},
                ],
            },
            {
                "key": "logo",
                "label": "Logo Image",
                "type": "image_swatch",
                "required": False,
                "is_active": True,
                "options": [
                    {"value": "star", "label": "Star", "price_delta": 0},
                    {"value": "moon", "label": "Moon", "price_delta": 20},
                ],
            },
            {
                "key": "gift_wrap",
                "label": "Gift Wrap",
                "type": "toggle",
                "required": False,
                "is_active": True,
            },
            {
                "key": "size",
                "label": "Size",
                "type": "slider",
                "required": False,
                "is_active": True,
                "min": 10,
                "max": 50,
            },
            {
                "key": "quantity",
                "label": "Quantity",
                "type": "number",
                "required": True,
                "is_active": True,
                "min": 1,
                "max": 10,
            },
            {
                "key": "custom_engraving",
                "label": "Custom Engraving",
                "type": "text_input",
                "required": False,
                "is_active": True,
            },
            {
                "key": "obsolete_feature",
                "label": "Obsolete Feature",
                "type": "select",
                "required": False,
                "is_active": False,
                "options": [
                    {"value": "old_val", "label": "Old Value", "price_delta": 0}
                ],
            },
        ]
    }


def test_valid_input(sample_category):
    selected = {
        "font": "bold",
        "primary_color": "blue",
        "logo": "star",
        "gift_wrap": True,
        "size": 25,
        "quantity": 5,
        "custom_engraving": "Hello World",
    }
    result = validate_attributes(sample_category, selected)
    assert result["valid"] is True
    assert result["errors"] == {}


def test_missing_required_field(sample_category):
    # 'font' is required but missing from selections
    selected = {
        "quantity": 5,
    }
    result = validate_attributes(sample_category, selected)
    assert result["valid"] is False
    assert "font" in result["errors"]
    assert result["errors"]["font"] == "This field is required."


def test_invalid_select(sample_category):
    selected = {
        "font": "italic",  # Not in option values
        "quantity": 5,
    }
    result = validate_attributes(sample_category, selected)
    assert result["valid"] is False
    assert "font" in result["errors"]
    assert result["errors"]["font"] == "Invalid option selected."


def test_invalid_color(sample_category):
    selected = {
        "font": "cursive",
        "primary_color": "green",  # Not in options
        "quantity": 5,
    }
    result = validate_attributes(sample_category, selected)
    assert result["valid"] is False
    assert "primary_color" in result["errors"]
    assert result["errors"]["primary_color"] == "Invalid option selected."


def test_invalid_image_swatch(sample_category):
    selected = {
        "font": "cursive",
        "logo": "sun",  # Not in options
        "quantity": 5,
    }
    result = validate_attributes(sample_category, selected)
    assert result["valid"] is False
    assert "logo" in result["errors"]
    assert result["errors"]["logo"] == "Invalid option selected."


def test_invalid_toggle(sample_category):
    # Must be bool, not integer/string/None
    for invalid_val in [1, 0, "True", "False", None]:
        selected = {
            "font": "cursive",
            "quantity": 5,
            "gift_wrap": invalid_val,
        }
        result = validate_attributes(sample_category, selected)
        assert result["valid"] is False
        assert "gift_wrap" in result["errors"]
        assert result["errors"]["gift_wrap"] == "Invalid value. Must be a boolean."


def test_slider_below_minimum(sample_category):
    selected = {
        "font": "cursive",
        "quantity": 5,
        "size": 9.9,  # min is 10
    }
    result = validate_attributes(sample_category, selected)
    assert result["valid"] is False
    assert "size" in result["errors"]
    assert "between 10 and 50" in result["errors"]["size"]


def test_slider_above_maximum(sample_category):
    selected = {
        "font": "cursive",
        "quantity": 5,
        "size": 50.1,  # max is 50
    }
    result = validate_attributes(sample_category, selected)
    assert result["valid"] is False
    assert "size" in result["errors"]
    assert "between 10 and 50" in result["errors"]["size"]


def test_slider_non_numeric(sample_category):
    # Test text or boolean input to slider/number
    for invalid_val in ["25", True, False, [25]]:
        selected = {
            "font": "cursive",
            "quantity": 5,
            "size": invalid_val,
        }
        result = validate_attributes(sample_category, selected)
        assert result["valid"] is False
        assert "size" in result["errors"]
        assert result["errors"]["size"] == "Value must be numeric."


def test_number_validation(sample_category):
    # Number works same as slider
    selected_below = {
        "font": "cursive",
        "quantity": 0,  # min is 1
    }
    result = validate_attributes(sample_category, selected_below)
    assert result["valid"] is False
    assert "quantity" in result["errors"]
    assert "between 1 and 10" in result["errors"]["quantity"]

    selected_above = {
        "font": "cursive",
        "quantity": 11,  # max is 10
    }
    result = validate_attributes(sample_category, selected_above)
    assert result["valid"] is False
    assert "quantity" in result["errors"]
    assert "between 1 and 10" in result["errors"]["quantity"]


def test_text_length_exceeded(sample_category):
    selected = {
        "font": "cursive",
        "quantity": 5,
        "custom_engraving": "A" * 61,  # 61 characters
    }
    result = validate_attributes(sample_category, selected)
    assert result["valid"] is False
    assert "custom_engraving" in result["errors"]
    assert result["errors"]["custom_engraving"] == "Maximum length exceeded."


def test_text_non_string(sample_category):
    selected = {
        "font": "cursive",
        "quantity": 5,
        "custom_engraving": 12345,  # non-string
    }
    result = validate_attributes(sample_category, selected)
    assert result["valid"] is False
    assert "custom_engraving" in result["errors"]
    assert result["errors"]["custom_engraving"] == "Value must be a string."


def test_unknown_key(sample_category):
    selected = {
        "font": "cursive",
        "quantity": 5,
        "unknown_field": "some_value",
    }
    result = validate_attributes(sample_category, selected)
    assert result["valid"] is False
    assert "unknown_field" in result["errors"]
    assert result["errors"]["unknown_field"] == "Unknown attribute"


def test_disabled_attribute(sample_category):
    selected = {
        "font": "cursive",
        "quantity": 5,
        "obsolete_feature": "old_val",  # obsolete_feature has is_active=False
    }
    result = validate_attributes(sample_category, selected)
    assert result["valid"] is False
    assert "obsolete_feature" in result["errors"]
    assert result["errors"]["obsolete_feature"] == "Attribute is disabled."


def test_none_and_malformed_inputs():
    # None parameters should not raise exception, but return error status
    result = validate_attributes(None, None)
    assert isinstance(result, dict)
    assert result["valid"] is True  # No attributes present, no required fields

    result = validate_attributes({}, {})
    assert result["valid"] is True

    # Malformed category schema
    result = validate_attributes({"attribute_schema": "invalid_type"}, {"key": "val"})
    assert result["valid"] is False
    assert "key" in result["errors"]
    assert result["errors"]["key"] == "Unknown attribute"
