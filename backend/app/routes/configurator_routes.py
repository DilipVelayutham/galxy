"""
GALXY E-Commerce Customization Platform
Configurator Routes

Provides canonical HTTP endpoints for attribute validation and real-time pricing calculation.
Enforces validation before pricing calculation and returns standardized API response shapes.
"""

from typing import Any, Dict, Optional
from flask import Blueprint, request, jsonify, current_app

from app.services.configurator_service import validate_attributes
from app.services.pricing_service import calculate_price

configurator_bp = Blueprint("configurator", __name__, url_prefix="/api/configurator")


def _get_document_by_id(collection_name: str, doc_id: Any, payload_dict: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Look up a MongoDB document by ID or extract directly from payload dict if passed during testing.
    Safely supports ObjectId and string identifiers.
    """
    if isinstance(payload_dict, dict) and payload_dict:
        return payload_dict

    if not doc_id:
        return None

    # Check Flask current_app database instances if configured
    db = None
    if hasattr(current_app, "db") and current_app.db is not None:
        db = current_app.db
    elif hasattr(current_app, "mongo") and hasattr(current_app.mongo, "db"):
        db = current_app.mongo.db
    elif current_app.config.get("DB") is not None:
        db = current_app.config["DB"]

    if db is not None:
        collection = getattr(db, collection_name, None) or db[collection_name]
        # Attempt lookup by string ID or ObjectId
        doc = collection.find_one({"_id": doc_id})
        if not doc:
            doc = collection.find_one({"id": doc_id})
        if not doc:
            try:
                from bson.objectid import ObjectId
                if ObjectId.is_valid(str(doc_id)):
                    doc = collection.find_one({"_id": ObjectId(str(doc_id))})
            except ImportError:
                pass
        return doc

    return None


@configurator_bp.route("/validate", methods=["POST"])
def validate_endpoint():
    """
    POST /api/configurator/validate
    Validates customer selected attributes against category schema.
    """
    data = request.get_json(silent=True) or {}
    category_id = data.get("category_id")
    selected_attributes = data.get("selected_attributes", {})

    category = _get_document_by_id("categories", category_id, data.get("category"))
    if not category:
        return jsonify({
            "success": False,
            "error": "Category not found"
        }), 404

    validation_result = validate_attributes(category, selected_attributes)
    return jsonify({
        "success": True,
        "data": validation_result
    }), 200


@configurator_bp.route("/price", methods=["POST"])
def price_endpoint():
    """
    POST /api/configurator/price
    Validates selection and computes authoritative live price and breakdown.
    """
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    category_id = data.get("category_id")
    selected_attributes = data.get("selected_attributes", {})
    quantity = data.get("quantity", 1)

    category = _get_document_by_id("categories", category_id, data.get("category"))
    product = _get_document_by_id("products", product_id, data.get("product"))

    if not category or not product:
        return jsonify({
            "success": False,
            "error": "Product or category not found"
        }), 404

    # Run validate_attributes FIRST internally
    validation_result = validate_attributes(category, selected_attributes)
    if not validation_result.get("valid", False):
        return jsonify({
            "success": False,
            "errors": validation_result.get("errors", {}),
            "data": validation_result
        }), 400

    pricing_result = calculate_price(product, category, selected_attributes, quantity)
    return jsonify({
        "success": True,
        "data": pricing_result
    }), 200
