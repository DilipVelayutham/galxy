from flask import Blueprint, request
from app.middleware.auth_middleware import require_admin
from app.services.testimonial_service import (
    get_all_testimonials_admin,
    create_testimonial,
    update_testimonial,
    delete_testimonial,
    reorder_testimonials,
    get_testimonial_by_id
)
from app.utils.response_helper import success_response, error_response

admin_testimonial_bp = Blueprint("admin_testimonials", __name__)

@admin_testimonial_bp.route("/api/admin/testimonials", methods=["GET"])
@require_admin
def admin_list_testimonials():
    """
    GET /api/admin/testimonials
    Admin route to list all testimonials with all fields (sorted by display_order).
    """
    try:
        data = get_all_testimonials_admin()
        return success_response(data)
    except Exception as e:
        return error_response(f"An error occurred while listing testimonials: {str(e)}")

@admin_testimonial_bp.route("/api/admin/testimonials/<string:id>", methods=["GET"])
@require_admin
def admin_get_testimonial(id):
    """
    GET /api/admin/testimonials/<id>
    Admin route to fetch a single testimonial by ID.
    """
    try:
        data = get_testimonial_by_id(id)
        if not data:
            return error_response("Testimonial not found", status_code=404)
        return success_response(data)
    except Exception as e:
        return error_response(f"An error occurred while fetching testimonial: {str(e)}")

@admin_testimonial_bp.route("/api/admin/testimonials", methods=["POST"])
@require_admin
def admin_create_testimonial():
    """
    POST /api/admin/testimonials
    Admin route to manually create a testimonial (source: 'manual').
    """
    try:
        body = request.get_json() or {}
        # Ensure source is 'manual' for manual entry
        body["source"] = "manual"
        body["review_id"] = None
        
        data = create_testimonial(body)
        return success_response(data, message="Testimonial created successfully", status_code=201)
    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        return error_response(f"An error occurred while creating testimonial: {str(e)}")

@admin_testimonial_bp.route("/api/admin/testimonials/<string:id>", methods=["PUT"])
@require_admin
def admin_update_testimonial(id):
    """
    PUT /api/admin/testimonials/<id>
    Admin route to edit any field of a testimonial.
    """
    try:
        body = request.get_json() or {}
        data = update_testimonial(id, body)
        return success_response(data, message="Testimonial updated successfully")
    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        return error_response(f"An error occurred while updating testimonial: {str(e)}")

@admin_testimonial_bp.route("/api/admin/testimonials/<string:id>", methods=["DELETE"])
@require_admin
def admin_delete_testimonial(id):
    """
    DELETE /api/admin/testimonials/<id>
    Admin route to hard delete a testimonial.
    """
    try:
        deleted = delete_testimonial(id)
        if not deleted:
            return error_response("Testimonial not found", status_code=404)
        return success_response(None, message="Testimonial deleted successfully")
    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        return error_response(f"An error occurred while deleting testimonial: {str(e)}")

@admin_testimonial_bp.route("/api/admin/testimonials/reorder", methods=["PUT"])
@require_admin
def admin_reorder_testimonials():
    """
    PUT /api/admin/testimonials/reorder
    Admin route for bulk reordering.
    Body format: { "order": [ { "testimonial_id": "...", "display_order": 1 } ] }
    """
    try:
        body = request.get_json() or {}
        order_list = body.get("order")
        if order_list is None:
            return error_response("Missing 'order' field in request body", status_code=400)
        reorder_testimonials(order_list)
        return success_response(None, message="Testimonials reordered successfully")
    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        return error_response(f"An error occurred while reordering testimonials: {str(e)}")
