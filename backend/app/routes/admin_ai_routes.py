import datetime
import logging
from flask import Blueprint, request, jsonify, g
from bson import ObjectId
from datetime import timezone

# Imports from both versions to support everything cleanly
from app.database import ai_generations
from app.utils.auth import admin_required
from app.models.ai_generation import get_all_generations_admin
from app.utils.auth_helpers import require_admin

logger = logging.getLogger(__name__)

# HEAD Blueprint:
admin_ai_blueprint = Blueprint('admin_ai_legacy', __name__)

# origin/main Blueprint:
admin_ai_bp = Blueprint("admin_ai", __name__, url_prefix="/api/admin/ai")


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


# ─── HEAD Routes ──────────────────────────────────────────────────────────────────

@admin_ai_blueprint.route('/api/admin/ai/generations', methods=['GET'])
@admin_required
def handle_get_admin_generations():
    """
    Admin-only analytics endpoint. Filters list by category, status, and date range.
    Uses high-performance cursor-based pagination.
    """
    limit = int(request.args.get("limit", 20))
    next_cursor = request.args.get("next_cursor")
    
    category_id = request.args.get("category_id")
    status = request.args.get("status")
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    
    query = {}
    
    if next_cursor:
        try:
            query["_id"] = {"$lt": ObjectId(next_cursor)}
        except Exception as e:
            print(f"[Admin Routes] Invalid next_cursor format: {e}")
            return jsonify({
                "success": False,
                "message": "Invalid next_cursor format. Must be a valid ObjectId."
            }), 400

    if category_id:
        try:
            query["category_id"] = ObjectId(category_id)
        except Exception:
            query["category_id"] = category_id
            
    if status:
        query["status"] = status
        
    if start_date_str or end_date_str:
        date_query = {}
        if start_date_str:
            try:
                date_query["$gte"] = datetime.datetime.fromisoformat(start_date_str)
            except ValueError:
                pass
        if end_date_str:
            try:
                date_query["$lte"] = datetime.datetime.fromisoformat(end_date_str)
            except ValueError:
                pass
        if date_query:
            query["created_at"] = date_query

    try:
        projection = {
            "_id": 1,
            "user_id": 1,
            "category_id": 1,
            "product_id": 1,
            "selected_attributes": 1,
            "output_image_url": 1,
            "status": 1,
            "error_message": 1,
            "generation_time_ms": 1,
            "created_at": 1
        }
        cursor = ai_generations.find(query, projection).sort("_id", -1).limit(limit)
        data = [clean_doc(doc) for doc in cursor]
        
        new_next_cursor = data[-1]["_id"] if data else None
        
        return jsonify({
            "success": True,
            "data": data,
            "limit": limit,
            "next_cursor": new_next_cursor,
            "has_more": len(data) == limit
        }), 200
        
    except Exception as e:
        print(f"[Admin Routes] Error fetching analytics data: {e}")
        return jsonify({
            "success": False,
            "message": f"Error fetching analytics data: {str(e)}"
        }), 500


# ─── origin/main Routes ───────────────────────────────────────────────────────────

@admin_ai_bp.route("/generations", methods=["GET"])
@require_admin
def list_all_generations():
    """
    Admin: full AI generation list, filterable by category, status, date range.
    Paginated. Powers the Module 12 admin analytics dashboard.
    """
    category_id = request.args.get("category_id")
    status = request.args.get("status")
    date_from_str = request.args.get("date_from")
    date_to_str = request.args.get("date_to")

    date_from = None
    date_to = None
    try:
        if date_from_str:
            date_from = datetime.datetime.fromisoformat(date_from_str).replace(
                tzinfo=timezone.utc
            )
        if date_to_str:
            date_to = datetime.datetime.fromisoformat(date_to_str).replace(
                tzinfo=timezone.utc
            )
    except ValueError:
        return jsonify({"success": False, "message": "Invalid date format. Use ISO8601."}), 400

    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(200, max(1, int(request.args.get("per_page", 50))))
    except (ValueError, TypeError):
        page, per_page = 1, 50

    generations, total = get_all_generations_admin(
        category_id=category_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        per_page=per_page,
    )

    return jsonify({
        "success": True,
        "data": {
            "generations": generations,
            "total": total,
            "page": page,
            "per_page": per_page,
        },
    }), 200

