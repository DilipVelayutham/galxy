from flask import Blueprint, request, jsonify, g
from utils.auth import login_required
from models.cart import serialize_doc
from services.cart_service import (
    get_or_create_cart,
    add_item,
    update_item,
    remove_item,
    clear
)

cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")

@cart_bp.route("", methods=["GET"])
@login_required
def api_get_cart():
    """
    GET /api/cart
    Returns the user's cart.
    """
    try:
        cart = get_or_create_cart(g.user_id)
        return jsonify({
            "success": True,
            "message": "Cart retrieved successfully.",
            "data": serialize_doc(cart)
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Failed to retrieve cart.",
            "errors": {"server": str(e)}
        }), 500

@cart_bp.route("/items", methods=["POST"])
@login_required
def api_add_item():
    """
    POST /api/cart/items
    Adds an item to the cart.
    """
    body = request.get_json() or {}
    product_id = body.get("product_id")
    selected_attributes = body.get("selected_attributes", {})
    custom_text = body.get("custom_text", "")
    quantity = body.get("quantity")
    
    if not product_id:
        return jsonify({
            "success": False,
            "message": "Failed to add item.",
            "errors": {"product_id": "product_id is required."}
        }), 400
        
    if quantity is None:
        quantity = 1
        
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Failed to add item.",
            "errors": {"quantity": "quantity must be an integer."}
        }), 400
        
    try:
        cart = add_item(g.user_id, product_id, selected_attributes, custom_text, quantity)
        return jsonify({
            "success": True,
            "message": "Item added to cart.",
            "data": serialize_doc(cart)
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "errors": {"validation": str(e)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Server error while adding item.",
            "errors": {"server": str(e)}
        }), 500

@cart_bp.route("/items/<item_id>", methods=["PUT"])
@login_required
def api_update_item(item_id):
    """
    PUT /api/cart/items/:item_id
    Updates item details (quantity, attributes, custom text).
    """
    body = request.get_json() or {}
    quantity = body.get("quantity")
    selected_attributes = body.get("selected_attributes")
    custom_text = body.get("custom_text")
    
    # Parse quantity if provided
    if quantity is not None:
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Failed to update item.",
                "errors": {"quantity": "quantity must be an integer."}
            }), 400
            
    try:
        cart = update_item(
            user_id=g.user_id,
            item_id=item_id,
            quantity=quantity,
            selected_attributes=selected_attributes,
            custom_text=custom_text
        )
        return jsonify({
            "success": True,
            "message": "Cart item updated successfully.",
            "data": serialize_doc(cart)
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "errors": {"validation": str(e)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Server error while updating item.",
            "errors": {"server": str(e)}
        }), 500

@cart_bp.route("/items/<item_id>", methods=["DELETE"])
@login_required
def api_remove_item(item_id):
    """
    DELETE /api/cart/items/:item_id
    Removes an item from the cart.
    """
    try:
        cart = remove_item(g.user_id, item_id)
        return jsonify({
            "success": True,
            "message": "Item removed from cart.",
            "data": serialize_doc(cart)
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "errors": {"validation": str(e)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Server error while removing item.",
            "errors": {"server": str(e)}
        }), 500

@cart_bp.route("/clear", methods=["DELETE"])
@login_required
def api_clear_cart():
    """
    DELETE /api/cart/clear
    Clears all items in the cart.
    """
    try:
        cart = clear(g.user_id)
        return jsonify({
            "success": True,
            "message": "Cart cleared successfully.",
            "data": serialize_doc(cart)
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Server error while clearing cart.",
            "errors": {"server": str(e)}
        }), 500
