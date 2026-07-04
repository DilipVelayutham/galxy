from flask import Blueprint, request, jsonify
from app.utils.auth import token_required, role_required
from app.services.review_service import ReviewService

admin_review_bp = Blueprint("admin_reviews", __name__)

@admin_review_bp.route("/reviews", methods=["GET"])
@token_required
@role_required(["admin"])
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
@role_required(["admin"])
def approve_review(id):
    """
    PUT /api/admin/reviews/:id/approve
    Approves a review, setting is_approved = true and triggering rating rollup.
    """
    result, status_code = ReviewService.approve_review(id)
    return jsonify(result), status_code


@admin_review_bp.route("/reviews/<id>/reject", methods=["PUT"])
@token_required
@role_required(["admin"])
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
@role_required(["admin"])
def delete_review(id):
    """
    DELETE /api/admin/reviews/:id
    Hard-deletes a review, triggering rollup if necessary.
    """
    result, status_code = ReviewService.delete_review(id)
    return jsonify(result), status_code


@admin_review_bp.route("/reviews/<id>/promote-to-testimonial", methods=["POST"])
@token_required
@role_required(["admin"])
def promote_to_testimonial(id):
    """
    POST /api/admin/reviews/:id/promote-to-testimonial
    Promotes a review to a testimonial.
    """
    result, status_code = ReviewService.promote_to_testimonial(id)
    return jsonify(result), status_code
