from flask import Blueprint, request, jsonify
from app.utils.auth import token_required, role_required
from app.services.review_service import ReviewService

admin_review_bp = Blueprint("admin_reviews", __name__)

@admin_review_bp.route("/reviews", methods=["GET"])
@token_required
@role_required(["admin", "super_admin"])
def get_admin_reviews():
    """
    GET /api/admin/reviews
    Retrieves all reviews for admin moderation.
    Supports query parameters: is_approved, product_id, page, limit
    """
    is_approved = request.args.get("is_approved")
    product_id = request.args.get("product_id")
    page = request.args.get("page", 1)
    limit = request.args.get("limit", 20)
    
    # Safely convert page and limit
    try:
        page = int(page)
    except ValueError:
        page = 1
        
    try:
        limit = int(limit)
    except ValueError:
        limit = 20
        
    result, status_code = ReviewService.get_admin_reviews(
        is_approved=is_approved,
        product_id=product_id,
        page=page,
        limit=limit
    )
    return jsonify(result), status_code


@admin_review_bp.route("/reviews/<id>/approve", methods=["PUT"])
@token_required
@role_required(["admin", "super_admin"])
def approve_review(id):
    """
    PUT /api/admin/reviews/:id/approve
    Approves a review, setting is_approved = true and triggering rating rollup.
    """
    result, status_code = ReviewService.approve_review(id)
    return jsonify(result), status_code


@admin_review_bp.route("/reviews/<id>/reject", methods=["PUT"])
@token_required
@role_required(["admin", "super_admin"])
def reject_review(id):
    """
    PUT /api/admin/reviews/:id/reject
    Rejects a review, saving optional reason and triggering rollup if needed.
    """
    # Accept optional reason from request body
    reason = None
    if request.is_json:
        data = request.get_json() or {}
        reason = data.get("reason")
    else:
        reason = request.form.get("reason")
        
    result, status_code = ReviewService.reject_review(id, reason=reason)
    return jsonify(result), status_code


@admin_review_bp.route("/reviews/<id>", methods=["DELETE"])
@token_required
@role_required(["admin", "super_admin"])
def delete_review(id):
    """
    DELETE /api/admin/reviews/:id
    Hard-deletes a review, triggering rollup if necessary.
    """
    result, status_code = ReviewService.delete_review(id)
    return jsonify(result), status_code


@admin_review_bp.route("/reviews/<id>/promote-to-testimonial", methods=["POST"])
@token_required
@role_required(["admin", "super_admin"])
def promote_to_testimonial(id):
    """
    POST /api/admin/reviews/:id/promote-to-testimonial
    Promotes an approved review to a testimonial.
    """
    customer_location = "Verified Buyer"
    display_order = 0
    
    if request.is_json:
        data = request.get_json() or {}
        customer_location = data.get("customer_location", "Verified Buyer")
        display_order = data.get("display_order", 0)
    else:
        customer_location = request.form.get("customer_location", "Verified Buyer")
        display_order = request.form.get("display_order", 0)

    errors = {}
    if not isinstance(customer_location, str) or len(customer_location.strip()) < 1 or len(customer_location.strip()) > 100:
        errors["customer_location"] = "Customer location must be a string between 1 and 100 characters."

    try:
        display_order_val = int(display_order)
        if display_order_val < 0:
            errors["display_order"] = "Display order must be a non-negative integer."
    except (ValueError, TypeError):
        errors["display_order"] = "Display order must be an integer."

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed",
            "errors": errors
        }), 400

    result, status_code = ReviewService.promote_to_testimonial(
        review_id=id,
        customer_location=customer_location,
        display_order=int(display_order)
    )
    return jsonify(result), status_code
