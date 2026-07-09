from flask import Blueprint, request, jsonify
from services.configurator_service import validate_attributes, calculate_price

configurator_bp = Blueprint("configurator", __name__, url_prefix="/api/configurator")

@configurator_bp.route("/validate", methods=["POST"])
def api_validate_attributes():
    """
    POST /api/configurator/validate
    Checks selected_attributes against the category's schema.
    """
    body = request.get_json() or {}
    category_id = body.get("category_id")
    selected_attributes = body.get("selected_attributes", {})
    
    if not category_id:
        return jsonify({
            "success": False,
            "message": "Validation failed.",
            "errors": {"category_id": "category_id is required."}
        }), 400
        
    try:
        validate_attributes(category_id, selected_attributes)
        return jsonify({
            "success": True,
            "message": "Attributes are valid.",
            "data": {"valid": True}
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "errors": {"selected_attributes": str(e)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Server error while validating attributes.",
            "errors": {"server": str(e)}
        }), 500

@configurator_bp.route("/price", methods=["POST"])
def api_calculate_price():
    """
    POST /api/configurator/price
    Calculates product base_price + attribute price_deltas.
    """
    body = request.get_json() or {}
    product_id = body.get("product_id")
    selected_attributes = body.get("selected_attributes", {})
    
    if not product_id:
        return jsonify({
            "success": False,
            "message": "Price calculation failed.",
            "errors": {"product_id": "product_id is required."}
        }), 400
        
    try:
        price_breakdown = calculate_price(product_id, selected_attributes)
        return jsonify({
            "success": True,
            "message": "Price calculated successfully.",
            "data": price_breakdown
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "errors": {"product_id": str(e)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Server error while calculating price.",
            "errors": {"server": str(e)}
        }), 500
