from flask import Blueprint, request, jsonify
from app.services.config_service import ConfigService

configurator_bp = Blueprint("configurator", __name__)

@configurator_bp.route("/validate", methods=["POST"])
def validate_configuration():
    data = request.get_json() or {}
    category_id = data.get("category_id")
    selected_attributes = data.get("selected_attributes", {})
    
    if not category_id:
        return jsonify({"success": False, "message": "category_id is required"}), 400
        
    is_valid, msg, result = ConfigService.validate_attributes(category_id, selected_attributes)
    if not is_valid:
        return jsonify({"success": False, "message": msg, "errors": result}), 422
        
    return jsonify({"success": True, "message": "Configuration is valid", "data": result}), 200

@configurator_bp.route("/price", methods=["POST"])
def calculate_configuration_price():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    selected_attributes = data.get("selected_attributes", {})
    
    if not product_id:
        return jsonify({"success": False, "message": "product_id is required"}), 400
        
    result, error = ConfigService.calculate_price(product_id, selected_attributes)
    if error:
        return jsonify({"success": False, "message": error}), 400
        
    return jsonify({"success": True, "data": result}), 200
