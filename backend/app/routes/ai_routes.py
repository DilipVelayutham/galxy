import datetime
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.services.ai_service import generate_preview
from app.database import ai_generations
from app.utils.auth import auth_required

ai_blueprint = Blueprint('ai', __name__)

def clean_doc(doc):
    """Helper to convert MongoDB ObjectIds to strings for JSON serialization."""
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])
    if "category_id" in doc and doc["category_id"]:
        doc["category_id"] = str(doc["category_id"])
    if "user_id" in doc and doc["user_id"]:
        doc["user_id"] = str(doc["user_id"])
    if "product_id" in doc and doc["product_id"]:
        doc["product_id"] = str(doc["product_id"])
    if "created_at" in doc and isinstance(doc["created_at"], datetime.datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    return doc

@ai_blueprint.route('/api/ai/generate-preview', methods=['POST'])
def handle_generate_preview():
    """Endpoint to generate an AI-rendered preview image of custom configurations."""
    body = request.get_json() or {}
    
    category_id = body.get("category_id")
    selected_attributes = body.get("selected_attributes")
    user_id = body.get("user_id")
    session_id = body.get("session_id")
    product_id = body.get("product_id")
    
    if not category_id:
        return jsonify({
            "success": False,
            "message": "category_id is required."
        }), 400
        
    if selected_attributes is None:
        return jsonify({
            "success": False,
            "message": "selected_attributes dictionary is required."
        }), 400

    # Extract client IP address, handling proxies via X-Forwarded-For
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address and ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()

    result = generate_preview(
        category_id=category_id,
        selected_attributes=selected_attributes,
        user_id=user_id,
        session_id=session_id,
        ip_address=ip_address,
        product_id=product_id
    )
    
    status_code = result.pop("status", 200)
    return jsonify(result), status_code

@ai_blueprint.route('/api/ai/generations/<user_id>', methods=['GET'])
@auth_required
def handle_get_user_history(user_id):
    """Retrieves paginated, date-descending successful generations for a user (auth-gated)."""
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    skip = (page - 1) * limit
    
    try:
        user_obj_id = ObjectId(user_id) if isinstance(user_id, str) and len(user_id) == 24 else user_id
        
        query = {
            "user_id": user_obj_id,
            "status": "success"
        }
        
        total = ai_generations.count_documents(query)
        projection = {
            "_id": 1,
            "product_id": 1,
            "category_id": 1,
            "selected_attributes": 1,
            "output_image_url": 1,
            "created_at": 1
        }
        cursor = ai_generations.find(query, projection).sort("created_at", -1).skip(skip).limit(limit)
        
        data = [clean_doc(doc) for doc in cursor]
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        
        return jsonify({
            "success": True,
            "data": data,
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": total_pages
        }), 200
        
    except Exception as e:
        print(f"[Routes] Error fetching user history: {e}")
        return jsonify({
            "success": False,
            "message": f"Error fetching history: {str(e)}"
        }), 500
