import math
from flask import jsonify

def success_response(data=None, message="", status_code=200):
    """
    Standard single-item or general success response shape.
    Format: { "success": true, "message": "...", "data": {} }
    """
    response = {
        "success": True,
        "message": message,
        "data": data if data is not None else {}
    }
    return jsonify(response), status_code

def paginated_response(data, page, limit, total, status_code=200):
    """
    Standard paginated list response shape.
    Format: { "success": true, "data": [], "page": 1, "limit": 20, "total": 0, "totalPages": 0 }
    """
    total_pages = math.ceil(total / limit) if limit > 0 else 0
    response = {
        "success": True,
        "data": data if data is not None else [],
        "page": int(page),
        "limit": int(limit),
        "total": int(total),
        "totalPages": total_pages
    }
    return jsonify(response), status_code

def error_response(message, errors=None, status_code=400):
    """
    Standard error response shape.
    Format: { "success": false, "message": "...", "errors": {} }
    """
    response = {
        "success": False,
        "message": message,
        "errors": errors if errors is not None else {}
    }
    return jsonify(response), status_code
