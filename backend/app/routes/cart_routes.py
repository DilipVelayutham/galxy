from flask import Blueprint, request, jsonify, g
from app.mocks.auth import require_auth
from app.services import cart_service
import datetime
from bson import ObjectId

cart_bp = Blueprint("cart", __name__)

def serialize_doc(doc):
    """
    Recursively converts BSON ObjectId and datetime objects to JSON-serializable formats.
    """
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime.datetime):
        return doc.isoformat()
    return doc

@cart_bp.route("", methods=["GET"])
@require_auth
def get_cart():
    user_id = g.user_id
    cart = cart_service.get_or_create_cart(user_id)
    return jsonify({
        "success": True,
        "data": serialize_doc(cart)
    }), 200

@cart_bp.route("/items", methods=["POST"])
@require_auth
def add_item():
    user_id = g.user_id
    data = request.get_json() or {}
    
    try:
        updated_cart = cart_service.add_item(user_id, data)
        return jsonify({
            "success": True,
            "message": "Added to cart",
            "data": serialize_doc(updated_cart)
        }), 201
    except FileNotFoundError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404
    except ValueError as e:
        if len(e.args) > 0:
            err_args = e.args[0]
            if isinstance(err_args, dict) and "errors" in err_args:
                return jsonify({
                    "success": False,
                    "message": err_args.get("message", "Invalid request"),
                    "errors": err_args.get("errors")
                }), 400
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

@cart_bp.route("/items/<item_id>", methods=["PUT"])
@require_auth
def update_item(item_id):
    user_id = g.user_id
    data = request.get_json() or {}
    
    try:
        updated_cart = cart_service.update_item(user_id, item_id, data)
        return jsonify({
            "success": True,
            "data": serialize_doc(updated_cart)
        }), 200
    except FileNotFoundError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404
    except ValueError as e:
        if len(e.args) > 0:
            err_args = e.args[0]
            if isinstance(err_args, dict) and "errors" in err_args:
                return jsonify({
                    "success": False,
                    "message": err_args.get("message", "Invalid request"),
                    "errors": err_args.get("errors")
                }), 400
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

@cart_bp.route("/items/<item_id>", methods=["DELETE"])
@require_auth
def remove_item(item_id):
    user_id = g.user_id
    try:
        updated_cart = cart_service.remove_item(user_id, item_id)
        return jsonify({
            "success": True,
            "message": "Item removed",
            "data": serialize_doc(updated_cart)
        }), 200
    except FileNotFoundError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404

@cart_bp.route("/clear", methods=["DELETE"])
@require_auth
def clear_cart():
    user_id = g.user_id
    updated_cart = cart_service.clear(user_id)
    return jsonify({
        "success": True,
        "message": "Cart cleared",
        "data": serialize_doc(updated_cart)
    }), 200
