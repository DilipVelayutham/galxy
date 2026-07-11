from flask import Blueprint, request, jsonify
from app.services.config_service import ConfigService
from app.services.configurator_service import validate_attributes
from app.services.pricing_service import calculate_price

configurator_bp = Blueprint("configurator", __name__)

@configurator_bp.route("/validate", methods=["POST"])
def validate_configuration():
    data = request.get_json() or {}
    
    # Check if full object is passed (for unit tests)
    if "category" in data:
        category = data["category"]
        selected_attributes = data.get("selected_attributes", {})
        val_res = validate_attributes(category, selected_attributes)
        return jsonify({
            "success": True,
            "message": "Configuration validation result",
            "data": {
                "valid": val_res["valid"],
                "errors": val_res["errors"]
            }
        }), 200
        
    category_id = data.get("category_id")
    selected_attributes = data.get("selected_attributes", {})
    
    if not category_id:
        return jsonify({"success": False, "message": "category_id is required"}), 400
        
    is_valid, msg, result = ConfigService.validate_attributes(category_id, selected_attributes)
    if not is_valid:
        return jsonify({"success": False, "message": msg, "errors": result}), 422
        
    return jsonify({
        "success": True,
        "message": "Configuration is valid",
        "data": {
            "valid": True,
            "errors": {},
            "validated": result
        }
    }), 200

@configurator_bp.route("/price", methods=["POST"])
def calculate_configuration_price():
    data = request.get_json() or {}
    
    # Check if full object is passed (for unit tests)
    if "product" in data and "category" in data:
        product = data["product"]
        category = data["category"]
        selected_attributes = data.get("selected_attributes", {})
        quantity = data.get("quantity", 1)
        
        # First validate
        val_res = validate_attributes(category, selected_attributes)
        if not val_res["valid"]:
            return jsonify({
                "success": False,
                "message": "Invalid attributes",
                "data": {
                    "valid": False,
                    "errors": val_res["errors"]
                }
            }), 400
            
        result = calculate_price(product, category, selected_attributes, quantity)
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    product_id = data.get("product_id")
    selected_attributes = data.get("selected_attributes", {})
    
    if not product_id:
        return jsonify({"success": False, "message": "product_id is required"}), 400
        
    result, error = ConfigService.calculate_price(product_id, selected_attributes)
    if error:
        return jsonify({"success": False, "message": error}), 400
        
    return jsonify({"success": True, "data": result}), 200
