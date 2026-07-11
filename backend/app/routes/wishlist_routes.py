from flask import Blueprint, jsonify, g, current_app, Response
from app.utils.auth import require_auth
from app.db import get_db
import app.services.wishlist_service as service
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import PyMongoError
from typing import Dict, Any, List

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/test/token', methods=['GET'])
def get_test_token():
    """
    GET /api/test/token
    Developer debug route to generate a valid long-expiration JWT token for local testing.
    Only active when current_app.debug or current_app.testing is True.
    """
    if not current_app.debug and not current_app.testing:
        return jsonify({
            "success": False,
            "message": "Only available in debug or testing environment"
        }), 403
        
    import jwt
    from datetime import datetime, timezone, timedelta
    
    secret = current_app.config.get('JWT_SECRET', 'galxy_default_jwt_secret_key_1234567890')
    user_id = "60c72b2f9b1d8e1f8c8b4560" # default test user ID
    payload = {
        "user_id": user_id,
        "username": "customer_sandbox",
        "role": "customer",
        "exp": datetime.now(timezone.utc) + timedelta(days=365) # 1 year expiration
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return jsonify({
        "success": True,
        "token": token,
        "user_id": user_id
    }), 200


@wishlist_bp.route('/wishlist', methods=['GET'])
@require_auth
def get_wishlist() -> Response:
    """
    GET /api/wishlist
    Returns the user's wishlist with fully hydrated product details.
    Gracefully handles inactive/deleted products.
    """
    user = g.current_user
    # Support both _id (member2) and user_id (develop)
    user_id = user.get('_id') or user.get('user_id')
    
    try:
        # Retrieve and hydrate the wishlist for the authenticated user via service layer
        # (maintaining strict controller/service separation)
        data = service.get_hydrated_wishlist(user_id)
        return jsonify({
            "success": True,
            "data": data
        }), 200
    except service.DatabaseErrorFetchingProducts as e:
        return jsonify({
            "success": False,
            "message": "Database error retrieving products"
        }), 500
    except PyMongoError as e:
        current_app.logger.error({
            "event": "database_error_retrieving_wishlist",
            "user_id": str(user_id),
            "error": str(e)
        }, exc_info=True)
        return jsonify({
            "success": False,
            "message": "Database error retrieving wishlist"
        }), 500
    except (TypeError, ValueError) as e:
        current_app.logger.error({
            "event": "invalid_user_id_error_retrieving_wishlist",
            "user_id": str(user_id),
            "error": str(e)
        }, exc_info=True)
        return jsonify({
            "success": False,
            "message": "Invalid user ID format"
        }), 400
    except KeyError as e:
        # KeyErrors during parsing (e.g. key missing in db record)
        current_app.logger.error({
            "event": "missing_id_in_product_document",
            "user_id": str(user_id),
            "error": str(e)
        }, exc_info=True)
        return jsonify({
            "success": False,
            "message": "Product document is missing standard fields"
        }), 500
    except Exception as e:
        # Final safety net for unexpected errors
        current_app.logger.error({
            "event": "unexpected_error_retrieving_wishlist",
            "user_id": str(user_id),
            "error": str(e)
        }, exc_info=True)
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred"
        }), 500


@wishlist_bp.route('/wishlist/<product_id>', methods=['POST'])
@require_auth
def add_to_wishlist(product_id) -> Response:
    """
    POST /api/wishlist/<product_id>
    Adds a product to the user's wishlist.
    Returns 404 if the product doesn't exist or is soft-deleted.
    """
    user = g.current_user
    user_id = user.get('_id') or user.get('user_id')
    try:
        count = service.add_to_wishlist(user_id, product_id)
        return jsonify({
            "success": True,
            "message": "Added to wishlist",
            "data": {
                "count": count
            }
        }), 200
    except ValueError as e:
        # According to the spec, returning 404 is required for missing/soft-deleted products.
        error_msg = str(e)
        return jsonify({
            "success": False,
            "message": error_msg
        }), 404
    except PyMongoError as e:
        current_app.logger.error({
            "event": "db_error_in_add_to_wishlist",
            "user_id": str(user_id),
            "product_id": str(product_id),
            "error": str(e)
        }, exc_info=True)
        return jsonify({
            "success": False,
            "message": "Database error adding product to wishlist"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@wishlist_bp.route('/wishlist/<product_id>', methods=['DELETE'])
@require_auth
def remove_from_wishlist(product_id) -> Response:
    """
    DELETE /api/wishlist/<product_id>
    Removes a product from the user's wishlist idempotently.
    """
    user = g.current_user
    user_id = user.get('_id') or user.get('user_id')
    try:
        count = service.remove_from_wishlist(user_id, product_id)
        return jsonify({
            "success": True,
            "message": "Removed from wishlist",
            "data": {
                "count": count
            }
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except PyMongoError as e:
        current_app.logger.error({
            "event": "db_error_in_remove_from_wishlist",
            "user_id": str(user_id),
            "product_id": str(product_id),
            "error": str(e)
        }, exc_info=True)
        return jsonify({
            "success": False,
            "message": "Database error removing product from wishlist"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@wishlist_bp.route('/wishlist/ids', methods=['GET'])
@require_auth
def get_wishlist_ids() -> Response:
    """
    GET /api/wishlist/ids
    Returns the flat list of product ID strings in the authenticated user's wishlist.
    """
    user = g.current_user
    user_id = user.get('_id') or user.get('user_id')
    try:
        ids = service.get_wishlist_ids(user_id)
        return jsonify({
            "success": True,
            "data": ids
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500
