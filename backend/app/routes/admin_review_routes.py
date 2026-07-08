# app/routes/admin_review_routes.py
from flask import Blueprint, request, jsonify, g
from app.middleware.auth import require_admin
from app.services.review_service import ReviewService
from app.services.testimonial_service import TestimonialService

admin_review_bp = Blueprint("admin_reviews", __name__)

@admin_review_bp.route("/reviews", methods=["GET"])
@require_admin
def get_admin_reviews():
    is_approved_str = request.args.get("is_approved")
    product_id_str = request.args.get("product_id")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    
    is_approved_bool = None
    if is_approved_str is not None:
        is_approved_bool = is_approved_str.lower() == "true"
        
    reviews, total, total_pages = ReviewService.get_admin_reviews(
        is_approved_bool, product_id_str, page, limit
    )
    
    return jsonify({
        "success": True,
        "data": reviews,
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages
    }), 200

@admin_review_bp.route("/reviews/<id>/approve", methods=["PUT"])
@require_admin
def approve_review(id):
    updated_review, err = ReviewService.approve_review(id)
    if err:
        return jsonify({"success": False, "message": err}), 404
        
    return jsonify({
        "success": True,
        "message": "Review approved successfully",
        "data": updated_review
    }), 200

@admin_review_bp.route("/reviews/<id>/reject", methods=["PUT"])
@require_admin
def reject_review(id):
    data = request.get_json() or {}
    reason = data.get("reason", "")
    
    success, err = ReviewService.reject_review(id, reason)
    if not success:
        return jsonify({"success": False, "message": err}), 404
        
    return jsonify({"success": True, "message": "Review rejected successfully"}), 200

@admin_review_bp.route("/reviews/<id>", methods=["DELETE"])
@require_admin
def delete_review(id):
    success, err = ReviewService.delete_review(id)
    if not success:
        return jsonify({"success": False, "message": err}), 404
        
    return jsonify({"success": True, "message": "Review hard deleted successfully"}), 200

@admin_review_bp.route("/reviews/<id>/promote-to-testimonial", methods=["POST"])
@require_admin
def promote_to_testimonial(id):
    data = request.get_json() or {}
    location = data.get("customer_location", "Chennai")
    display_order = data.get("display_order", 0)
    
    new_testimonial, err = TestimonialService.promote_from_review(id, location, display_order)
    if err:
        return jsonify({"success": False, "message": err}), 400
        
    return jsonify({
        "success": True,
        "message": "Review promoted to testimonial successfully",
        "data": new_testimonial
    }), 201
