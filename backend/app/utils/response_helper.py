from flask import jsonify

def success_response(data, message="", status_code=200):
    """Standard success API response helper for Galxy."""
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code

def error_response(message, errors=None, status_code=400):
    """Standard error API response helper for Galxy."""
    if errors is None:
        errors = {}
    response = {
        "success": False,
        "message": message,
        "errors": errors
    }
    return jsonify(response), status_code
