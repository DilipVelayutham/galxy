from flask import Blueprint, request, jsonify, g
from datetime import datetime
import logging
from app.services import site_content_service
import os

from app.middleware.auth import require_admin

from app.utils.content_schema_validator import validate_content, SECTION_ENUM

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin_site_content', __name__)

def serialize_document(doc):
    """Utility to make MongoDB document JSON serializable."""
    if not doc:
        return None
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    if "updated_at" in d and isinstance(d["updated_at"], datetime):
        d["updated_at"] = d["updated_at"].isoformat()
    return d

@admin_bp.route('/api/admin/site-content/<section>', methods=['GET'])
@require_admin
def admin_get_section(section, current_user):
    """
    GET /api/admin/site-content/:section
    Same as public GET, but protected under admin dashboard scope.
    """
    if section not in SECTION_ENUM:
        return jsonify({
            "success": False,
            "data": None,
            "message": f"Unknown section '{section}'."
        }), 404

    try:
        doc = site_content_service.get_section(section)
        if not doc:
            return jsonify({
                "success": False,
                "data": None,
                "message": f"Section '{section}' has not been seeded or initialized yet."
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "section": doc["section"],
                "content": doc.get("content", {})
            }
        }), 200
    except Exception as e:
        logger.error(f"Error in admin get section {section}: {e}")
        return jsonify({
            "success": False,
            "data": None,
            "message": "An error occurred while fetching content."
        }), 500


@admin_bp.route('/api/admin/site-content/<section>', methods=['PUT'])
@require_admin
def admin_update_section(section, current_user):
    """
    PUT /api/admin/site-content/:section
    Body: { "content": {...} }
    Updates content of a specific section after validating its shape.
    """
    if section not in SECTION_ENUM:
        return jsonify({
            "success": False,
            "message": f"Unknown section '{section}'.",
            "errors": {"section": "Unknown section"}
        }), 404

    body = request.get_json(silent=True)
    if not body or "content" not in body:
        return jsonify({
            "success": False,
            "message": "Missing 'content' field in request body.",
            "errors": {"content": "Field is required"}
        }), 400

    content = body["content"]
    
    # Run content validation
    is_valid, errors = validate_content(section, content)
    if not is_valid:
        return jsonify({
            "success": False,
            "message": "Content schema validation failed.",
            "errors": errors
        }), 400

    try:
        admin_user_id = current_user.get('user_id', 'unknown_admin')
        updated_doc = site_content_service.update_section(section, content, admin_user_id)
        
        return jsonify({
            "success": True,
            "message": "Content updated",
            "data": {
                "section": updated_doc["section"],
                "content": updated_doc.get("content", {})
            }
        }), 200
    except Exception as e:
        logger.error(f"Error updating section {section}: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to update content due to database error.",
            "errors": {"database": str(e)}
        }), 500
