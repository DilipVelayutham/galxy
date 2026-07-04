<<<<<<< HEAD
import datetime
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.database import ai_generations
from app.utils.auth import admin_required

admin_ai_blueprint = Blueprint('admin_ai', __name__)

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

@admin_ai_blueprint.route('/api/admin/ai/generations', methods=['GET'])
@admin_required
def handle_get_admin_generations():
    """
    Admin-only analytics endpoint. Filters list by category, status, and date range.
    Uses high-performance cursor-based pagination.
    """
    # Pagination
    limit = int(request.args.get("limit", 20))
    next_cursor = request.args.get("next_cursor") # ObjectId representing the cursor position
    
    # Filtering parameters
    category_id = request.args.get("category_id")
    status = request.args.get("status")
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    
    query = {}
    
    # 1. Apply cursor constraints (older documents have smaller ObjectIds)
    if next_cursor:
        try:
            query["_id"] = {"$lt": ObjectId(next_cursor)}
        except Exception as e:
            print(f"[Admin Routes] Invalid next_cursor format: {e}")
            return jsonify({
                "success": False,
                "message": "Invalid next_cursor format. Must be a valid ObjectId."
            }), 400

    # 2. Apply general filters
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
        # Cursor pagination: sort by _id descending, limit to requested size
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
        
        # Determine the cursor for the next page (the ID of the last item returned)
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
=======
"""
admin_ai_routes.py — Module 5 AI Preview Generation
Admin-only routes for AI usage analytics.

OWNER: Backend Member 2 (Gokul — T4)
This file implements the full administrative route logic.

Routes:
  GET /api/admin/ai/generations
      Full list, filterable by category/status/date, paginated.
      Powers the admin AI-usage analytics view (Module 12 dashboard).

GUARDRAIL: Do NOT implement PUT /api/admin/categories/:id/ai-prompt-template here.
That route belongs to Module 2 (which owns category writes). See spec §9 note.
"""
import logging
from flask import Blueprint, request, jsonify, g
from datetime import datetime, timezone

from app.models.ai_generation import get_all_generations_admin
from app.utils.auth_helpers import require_admin

logger = logging.getLogger(__name__)

admin_ai_bp = Blueprint("admin_ai", __name__, url_prefix="/api/admin/ai")


@admin_ai_bp.route("/generations", methods=["GET"])
@require_admin
def list_all_generations():
    """
    Admin: full AI generation list, filterable by category, status, date range.
    Paginated. Powers the Module 12 admin analytics dashboard.

    Query params:
        category_id  (str, optional)
        status       (str, optional: "success" | "failed" | "rate_limited")
        date_from    (str, optional: ISO8601)
        date_to      (str, optional: ISO8601)
        page         (int, default 1)
        per_page     (int, default 50, max 200)
    """
    category_id = request.args.get("category_id")
    status = request.args.get("status")
    date_from_str = request.args.get("date_from")
    date_to_str = request.args.get("date_to")

    date_from = None
    date_to = None
    try:
        if date_from_str:
            date_from = datetime.fromisoformat(date_from_str).replace(
                tzinfo=timezone.utc
            )
        if date_to_str:
            date_to = datetime.fromisoformat(date_to_str).replace(
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
>>>>>>> origin/main
