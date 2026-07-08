# app/routes/review_routes.py
from flask import Blueprint, request, jsonify, g
from app.middleware.auth import require_auth
from app.services.review_service import ReviewService

review_bp = Blueprint("reviews", __name__)

@review_bp.route("/products/<product_id>/reviews", methods=["GET"])
def get_product_reviews(product_id):
    sort_by = request.args.get("sort", "newest")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    
    formatted_reviews, total, total_pages = ReviewService.get_product_reviews(
        product_id, sort_by, page, limit
    )
    
    return jsonify({
        "success": True,
        "data": formatted_reviews,
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages
    }), 200

@review_bp.route("/products/<product_id>/reviews", methods=["POST"])
@require_auth
def submit_review(product_id):
    user_id = g.user["id"]
    data = request.get_json() or {}
    rating = data.get("rating")
    comment = data.get("comment", "")
    images = data.get("images", [])
    
    if not rating or not (1 <= int(rating) <= 5):
        return jsonify({"success": False, "message": "Rating must be an integer between 1 and 5"}), 400
        
    review, msg, code = ReviewService.create_review(
        user_id, product_id, rating, comment, images
    )
    
    if code != 201:
        return jsonify({"success": False, "message": msg}), code
        
    return jsonify({
        "success": True,
        "message": msg,
        "data": review
    }), 201
