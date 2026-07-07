from flask import Blueprint, request, jsonify

from app.utils.auth_middleware import require_auth
from app.services import user_service, address_service
from app.models.address import ValidationError
from app.models.user import to_public_dict

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """
    GET /api/user/profile
    Returns name, email, phone, and addresses list of the authenticated user.
    """
    profile = to_public_dict(request.user)
    trimmed_profile = {
        "name": profile.get("name"),
        "email": profile.get("email"),
        "phone": profile.get("phone"),
        "addresses": profile.get("addresses")
    }
    return jsonify({
        "success": True,
        "message": "Profile retrieved successfully.",
        "data": trimmed_profile
    }), 200

@user_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """
    PUT /api/user/profile
    Updates profile fields (name, phone). Explicitly blocks email updates.
    """
    data = request.get_json() or {}
    try:
        updated_user = user_service.update_profile(request.user['_id'], data)
        profile = to_public_dict(updated_user)
        trimmed_profile = {
            "name": profile.get("name"),
            "email": profile.get("email"),
            "phone": profile.get("phone"),
            "addresses": profile.get("addresses")
        }
        return jsonify({
            "success": True,
            "message": "Profile updated successfully.",
            "data": trimmed_profile
        }), 200
    except ValidationError as e:
        return jsonify({
            "success": False,
            "message": "Validation failed.",
            "errors": e.errors
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}",
            "errors": {}
        }), 500

@user_bp.route('/addresses', methods=['POST'])
@require_auth
def add_address():
    """
    POST /api/user/addresses
    Adds a new address to the authenticated user.
    """
    data = request.get_json() or {}
    try:
        new_address = address_service.add_address(request.user['_id'], data)
        # Convert ObjectId in address response to string
        new_address['_id'] = str(new_address['_id'])
        return jsonify({
            "success": True,
            "message": "Address added successfully.",
            "data": new_address
        }), 201
    except ValidationError as e:
        return jsonify({
            "success": False,
            "message": "Validation failed.",
            "errors": e.errors
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}",
            "errors": {}
        }), 500

@user_bp.route('/addresses/<address_id>', methods=['PUT'])
@require_auth
def update_address(address_id):
    """
    PUT /api/user/addresses/:id
    Updates an existing address of the authenticated user. Partial updates allowed.
    """
    data = request.get_json() or {}
    try:
        updated_addr = address_service.update_address(request.user['_id'], address_id, data)
        # Convert ObjectId in address response to string
        updated_addr['_id'] = str(updated_addr['_id'])
        return jsonify({
            "success": True,
            "message": "Address updated successfully.",
            "data": updated_addr
        }), 200
    except ValidationError as e:
        return jsonify({
            "success": False,
            "message": "Validation failed.",
            "errors": e.errors
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}",
            "errors": {}
        }), 500

@user_bp.route('/addresses/<address_id>', methods=['DELETE'])
@require_auth
def delete_address(address_id):
    """
    DELETE /api/user/addresses/:id
    Removes an address of the authenticated user. Subject to invariants constraint.
    """
    try:
        address_service.delete_address(request.user['_id'], address_id)
        return jsonify({
            "success": True,
            "message": "Address deleted successfully.",
            "data": {}
        }), 200
    except ValidationError as e:
        return jsonify({
            "success": False,
            "message": "Validation failed.",
            "errors": e.errors
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}",
            "errors": {}
        }), 500
