from flask import Blueprint, jsonify, request
from app.utils.auth_middleware import require_auth
from app.models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    # request.user is attached by the @require_auth decorator
    user = request.user
    return jsonify({
        "success": True,
        "data": User.to_public_dict(user)
    }), 200

@user_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    # In2 (Naresh) will implement profile updates (name, phone). Email updates rejected.
    return jsonify({
        "success": True,
        "message": "Profile updated",
        "data": User.to_public_dict(request.user)
    }), 200

@user_bp.route('/addresses', methods=['POST'])
@require_auth
def add_address():
    # In2 (Naresh) will implement this.
    return jsonify({
        "success": True,
        "message": "Address added",
        "data": {}
    }), 201

@user_bp.route('/addresses/<address_id>', methods=['PUT', 'DELETE'])
@require_auth
def manage_address(address_id):
    # In2 (Naresh) will implement this.
    if request.method == 'DELETE':
        return jsonify({
            "success": True,
            "message": "Address deleted"
        }), 200
    else:
        return jsonify({
            "success": True,
            "message": "Address updated",
            "data": {}
        }), 200
