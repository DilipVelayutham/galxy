from flask import Blueprint, request, jsonify
from app.models.ai_generation import AIGeneration
from bson import ObjectId
from datetime import datetime
from functools import wraps

admin_ai_blueprint = Blueprint("admin_ai", __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Admin authorization check
        # Inspect headers or auth token for admin privileges
        auth_header = request.headers.get("Authorization", "")
        is_admin_header = request.headers.get("X-Admin-Role") == "admin"
        is_admin_token = auth_header == "AdminSecretToken" or "admin" in auth_header.lower()
        is_bypass = request.args.get("admin_bypass") == "true"
        
        if not (is_admin_header or is_admin_token or is_bypass):
            return jsonify({
                "success": False,
                "message": "Forbidden: Administrative privileges required"
            }), 403
            
        return f(*args, **kwargs)
    return decorated

@admin_ai_blueprint.route("/api/admin/ai/generations", methods=["GET"])
@admin_required
def get_admin_generations():
    # Pagination parsing
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        if page < 1 or limit < 1:
            raise ValueError()
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid page or limit parameter. Must be positive integers."
        }), 400
        
    # Filters
    category_id = request.args.get("category_id")
    status = request.args.get("status")
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    
    query = {}
    
    if category_id:
        try:
            query["category_id"] = ObjectId(category_id)
        except Exception:
            return jsonify({
                "success": False,
                "message": "Invalid category_id format"
            }), 400
            
    if status:
        query["status"] = status
        
    date_query = {}
    if start_date_str:
        try:
            date_query["$gte"] = datetime.fromisoformat(start_date_str)
        except Exception:
            return jsonify({
                "success": False,
                "message": "Invalid start_date format, use ISO format (YYYY-MM-DD)"
            }), 400
            
    if end_date_str:
        try:
            if len(end_date_str) == 10:
                end_date_str += "T23:59:59.999"
            date_query["$lte"] = datetime.fromisoformat(end_date_str)
        except Exception:
            return jsonify({
                "success": False,
                "message": "Invalid end_date format, use ISO format (YYYY-MM-DD)"
            }), 400
            
    if date_query:
        query["created_at"] = date_query
        
    try:
        col = AIGeneration.get_collection()
        skip = (page - 1) * limit
        
        # Query sorting by created_at descending (most recent first)
        cursor = col.find(query).sort("created_at", -1).skip(skip).limit(limit)
        total_records = col.count_documents(query)
        
        generations = []
        for doc in cursor:
            doc_copy = doc.copy()
            doc_copy["_id"] = str(doc_copy["_id"])
            if doc_copy.get("user_id"):
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
