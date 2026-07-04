from flask import Blueprint, request, jsonify, g
from app.utils.auth import token_required
from app.services.review_service import ReviewService

review_bp = Blueprint("reviews", __name__)

@review_bp.route("/products/<id>/reviews", methods=["POST"])
@token_required
def submit_review(id):
    """
    POST /api/products/:id/reviews
    Submits a review for a product. Require authenticated user.
    """
    user_id = g.user_id
    product_id = id
    
    # Support both JSON and multipart/form-data request payloads
    if request.is_json:
        data = request.get_json() or {}
        order_id = data.get("order_id")
        order_number = data.get("order_number")
        rating = data.get("rating")
        comment = data.get("comment", "")
        images = data.get("images", [])
    else:
        # Form data submission
        data = request.form
        order_id = data.get("order_id")
        order_number = data.get("order_number")
        rating = data.get("rating")
        comment = data.get("comment", "")
        # Grab uploaded files from the request (if any)
        images = request.files.getlist("images") or request.files.getlist("images[]") or []

    # Input validations
    errors = {}
    if not order_id:
        errors["order_id"] = "Order ID is required."
    if not order_number:
        errors["order_number"] = "Order number is required."
    if rating is None:
        errors["rating"] = "Rating is required."
    else:
        try:
            rating_val = int(rating)
            if rating_val < 1 or rating_val > 5:
                errors["rating"] = "Rating must be between 1 and 5."
        except ValueError:
            errors["rating"] = "Rating must be an integer."

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed",
            "errors": errors
        }), 400

    # Business Logic
    result, status_code = ReviewService.submit_review(
        product_id=product_id,
        user_id=user_id,
        order_id=order_id,
        order_number=order_number,
        rating=int(rating),
        comment=comment,
        images=images
    )
    
    return jsonify(result), status_code


@review_bp.route("/products/<id>/reviews", methods=["GET"])
def get_product_reviews(id):
    """
    GET /api/products/:id/reviews
    Retrieves only approved reviews for a product.
    Supports query parameters: page, limit, sort
    """
    page = request.args.get("page", 1)
    limit = request.args.get("limit", 20)
    sort = request.args.get("sort", "newest")
    
    # Safely convert page and limit
    try:
        page = int(page)
    except ValueError:
        page = 1
        
    try:
        limit = int(limit)
    except ValueError:
        limit = 20
        
    # Validate sort parameter
    valid_sorts = {"newest", "highest_rated", "lowest_rated"}
    if sort not in valid_sorts:
        sort = "newest"
        
    result, status_code = ReviewService.get_product_reviews(
        product_id=id,
        page=page,
        limit=limit,
        sort=sort
    )
    
    return jsonify(result), status_code
