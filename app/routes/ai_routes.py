from flask import Blueprint, request, jsonify, g
from app.services.ai_service import orchestrate_generation
from functools import wraps

ai_blueprint = Blueprint("ai", __name__)

def optional_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Support X-User-Id header or user_id in the JSON body for test runs/guest emulation
        g.user_id = request.headers.get("X-User-Id")
        if not g.user_id and request.is_json:
            g.user_id = request.json.get("user_id")
        return f(*args, **kwargs)
    return decorated

@ai_blueprint.route("/api/ai/generate-preview", methods=["POST"])
@optional_login
def generate_preview():
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "Content-Type must be application/json"
        }), 400
        
    body = request.json
    category_id = body.get("category_id")
    product_id = body.get("product_id")
    selected_attributes = body.get("selected_attributes")
    session_id = body.get("session_id")
    input_reference_image = body.get("input_reference_image")
    
    # 1. Base input field validation
    if not category_id:
        return jsonify({
            "success": False,
            "message": "Missing required field: category_id"
        }), 400
        
    if selected_attributes is None:
        return jsonify({
            "success": False,
            "message": "Missing required field: selected_attributes"
        }), 400
        
    user_id = getattr(g, "user_id", None)
    
    # 2. Check that guest session ID is present if not logged in
    if not user_id and not session_id:
        return jsonify({
            "success": False,
            "message": "Missing guest identifier: session_id or user authentication required"
        }), 400
        
    # 3. Call orchestrator service
    result = orchestrate_generation(
        category_id=category_id,
        product_id=product_id,
        selected_attributes=selected_attributes,
        session_id=session_id,
        user_id=user_id,
        input_reference_image=input_reference_image
    )
    
    # 4. Format output responses
    status_code = result.get("status_code", 200)
    response_body = {
        "success": result.get("success", False)
    }
    
    if "message" in result:
        response_body["message"] = result["message"]
        
    if "errors" in result:
        response_body["errors"] = result["errors"]
        
    if "data" in result:
        response_body["data"] = result["data"]
        
    return jsonify(response_body), status_code
