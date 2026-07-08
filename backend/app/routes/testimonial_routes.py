from flask import Blueprint
from app.services.testimonial_service import get_public_testimonials
from app.utils.response_helper import success_response, error_response

testimonial_bp = Blueprint("public_testimonials", __name__)

@testimonial_bp.route("/api/testimonials", methods=["GET"])
def list_testimonials():
    """
    GET /api/testimonials
    Returns only is_active: True testimonials sorted by display_order.
    Excludes review_id and is_active to match Galxy public contract.
    """
    try:
        data = get_public_testimonials()
        return success_response(data)
    except Exception as e:
        return error_response(f"An error occurred while retrieving testimonials: {str(e)}")
