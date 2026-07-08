# app/routes/testimonial_routes.py
from flask import Blueprint, jsonify
from app.services.testimonial_service import TestimonialService

testimonial_bp = Blueprint("testimonials", __name__)

@testimonial_bp.route("/testimonials", methods=["GET"])
def get_testimonials():
    testimonials = TestimonialService.get_active_testimonials()
    return jsonify({
        "success": True,
        "data": testimonials
    }), 200
