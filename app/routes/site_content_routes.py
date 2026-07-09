from flask import Blueprint, request, jsonify
import logging
from app.services import site_content_service
from app.utils.content_schema_validator import SECTION_ENUM

logger = logging.getLogger(__name__)

public_bp = Blueprint('public_site_content', __name__)

@public_bp.route('/api/site-content', methods=['GET'])
def get_bulk_sections():
    """
    GET /api/site-content?sections=hero,footer,social_links
    Retrieve multiple sections in bulk.
    """
    sections_param = request.args.get('sections')
    if not sections_param:
        return jsonify({
            "success": False,
            "data": None,
            "message": "Missing 'sections' query parameter. Usage: /api/site-content?sections=hero,footer"
        }), 400

    sections_list = [s.strip() for s in sections_param.split(',') if s.strip()]
    
    # Filter only valid sections, silently dropping invalid/unknown ones (F3)
    valid_sections = [s for s in sections_list if s in SECTION_ENUM]
    if not valid_sections:
        return jsonify({
            "success": True,
            "data": {}
        }), 200

    try:
        bulk_data = site_content_service.get_bulk(valid_sections)
        return jsonify({
            "success": True,
            "data": bulk_data
        }), 200
    except Exception as e:
        logger.error(f"Error fetching bulk sections: {e}")
        return jsonify({
            "success": False,
            "data": None,
            "message": "An error occurred while fetching content."
        }), 500


@public_bp.route('/api/site-content/<section>', methods=['GET'])
def get_single_section(section):
    """
    GET /api/site-content/:section
    Retrieve a single section.
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
        logger.error(f"Error fetching section {section}: {e}")
        return jsonify({
            "success": False,
            "data": None,
            "message": "An error occurred while fetching content."
        }), 500
