from flask import Blueprint, request, jsonify, g
from app.services.ai_service import orchestrate_generation
from functools import wraps
from datetime import datetime

ai_blueprint = Blueprint("ai", __name__)

def optional_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # NOTE: This is a placeholder mock authentication parser for testing/development.
        # It relies on unsecured headers (X-User-Id) and JSON body fields to identify users.
        # Before production deployment, this must be consolidated with the actual JWT-based 
        # Auth Middleware (Module 1).
        g.user_id = request.headers.get("X-User-Id")
        if not g.user_id and request.is_json:
            try:
                # Use silent=True to handle cases where request body might not be JSON or empty
                body = request.get_json(silent=True)
                if body:
                    g.user_id = body.get("user_id")
            except Exception:
                pass
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

@ai_blueprint.route("/api/ai/generations/<user_id>", methods=["GET"])
@optional_login
def get_user_generations(user_id):
    # Enforce request.user._id matching (must match authenticated user_id in context or be admin)
    auth_user_id = getattr(g, "user_id", None)
    is_admin = request.headers.get("X-Admin-Role") == "admin" or request.headers.get("Authorization") == "Bearer mock-admin-token-123"
    
    if not auth_user_id and not is_admin:
        return jsonify({
            "success": False,
            "message": "Unauthorized: Authentication required"
        }), 401
        
    if auth_user_id != user_id and not is_admin:
        return jsonify({
            "success": False,
            "message": "Forbidden: You do not have permission to view this user's design history."
        }), 403
        
    # Pagination parameters
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        if page < 1 or limit < 1:
            raise ValueError()
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid page or limit parameters. Must be positive integers."
        }), 400
        
    try:
        from app.models.ai_generation import AIGeneration
        from bson import ObjectId
        
        col = AIGeneration.get_collection()
        skip = (page - 1) * limit
        
        query = {
            "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
            "status": "success"  # Show only successfully generated custom designs
        }
        
        cursor = col.find(query).sort("created_at", -1).skip(skip).limit(limit)
        total_records = col.count_documents(query)
        
        generations = []
        for doc in cursor:
            doc_copy = doc.copy()
            doc_copy["_id"] = str(doc_copy["_id"])
            doc_copy["user_id"] = str(doc_copy["user_id"])
            if doc_copy.get("category_id"):
                doc_copy["category_id"] = str(doc_copy["category_id"])
            if doc_copy.get("product_id"):
                doc_copy["product_id"] = str(doc_copy["product_id"])
            if isinstance(doc_copy.get("created_at"), datetime):
                doc_copy["created_at"] = doc_copy["created_at"].isoformat()
            generations.append(doc_copy)
            
        return jsonify({
            "success": True,
            "data": {
                "generations": generations,
                "pagination": {
                    "total": total_records,
                    "page": page,
                    "limit": limit,
                    "pages": (total_records + limit - 1) // limit if total_records else 1
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Database error: {str(e)}"
        }), 500
