# app/routes/admin_testimonial_routes.py
from flask import Blueprint, request, jsonify
from app.middleware.auth import require_admin
from app.services.testimonial_service import TestimonialService

admin_testimonial_bp = Blueprint("admin_testimonials", __name__)

@admin_testimonial_bp.route("/testimonials", methods=["POST"])
@require_admin
def create_testimonial():
    data = request.get_json() or {}
    name = data.get("customer_name")
    quote = data.get("quote")
    location = data.get("customer_location", "")
    rating = data.get("rating", 5)
    image = data.get("image")
    display_order = data.get("display_order", 0)
    is_active = data.get("is_active", True)
    
    if not name or not quote:
        return jsonify({"success": False, "message": "customer_name and quote are required"}), 400
        
    new_t = TestimonialService.create_manual_testimonial(
        name, quote, location, rating, image, display_order, is_active
    )
    
    return jsonify({
        "success": True,
        "message": "Testimonial created manually",
        "data": new_t
    }), 201

@admin_testimonial_bp.route("/testimonials/<id>", methods=["PUT"])
@require_admin
def update_testimonial(id):
    data = request.get_json() or {}
    success = TestimonialService.update_testimonial(id, data)
    if not success:
        return jsonify({"success": False, "message": "Testimonial not found"}), 404
        
    return jsonify({"success": True, "message": "Testimonial updated successfully"}), 200

@admin_testimonial_bp.route("/testimonials/<id>", methods=["DELETE"])
@require_admin
def delete_testimonial(id):
    success = TestimonialService.delete_testimonial(id)
    if not success:
        return jsonify({"success": False, "message": "Testimonial not found"}), 404
        
    return jsonify({"success": True, "message": "Testimonial deleted successfully"}), 200

@admin_testimonial_bp.route("/testimonials/reorder", methods=["PUT"])
@require_admin
def reorder_testimonials():
    data = request.get_json() or {}
    orders = data.get("order", [])
    
    TestimonialService.reorder_testimonials(orders)
    return jsonify({"success": True, "message": "Testimonials reordered successfully"}), 200
