from flask import Blueprint, jsonify, request
from app.utils.auth_middleware import require_auth
from app.services.user_service import UserService, UserServiceError

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    try:
        # request.user is attached by the @require_auth decorator
        user_id = request.user["_id"]
        profile_data = UserService.get_profile(user_id)
        return jsonify({
            "success": True,
            "data": profile_data
        }), 200
    except UserServiceError as e:
        return jsonify({
            "success": False,
            "message": e.message,
            "errors": {}
        }), e.status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "errors": {}
        }), 500

@user_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    # In2 (Naresh) will implement profile updates (name, phone). Email updates rejected.
    try:
        user_id = request.user["_id"]
        profile_data = UserService.get_profile(user_id)
        return jsonify({
            "success": True,
            "message": "Profile updated",
            "data": profile_data
        }), 200
    except UserServiceError as e:
        return jsonify({
            "success": False,
            "message": e.message,
            "errors": {}
        }), e.status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "errors": {}
        }), 500

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
