<<<<<<< HEAD
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
=======
"""
ai_routes.py — Module 5 AI Preview Generation
Flask Blueprint for all AI Preview routes.

ROUTE OWNERSHIP:
  POST /api/ai/generate-preview         ← Backend Member 1 (T1, this file)
  GET  /api/ai/generations/:user_id     ← Backend Member 2 (T4, this file)

Both routes are fully implemented and integrated.
"""
import logging
from flask import Blueprint, request, jsonify, g

from app.services.ai_service import generate_preview
from app.models.ai_generation import get_user_generations, count_user_generations
from app.utils.auth_helpers import optional_auth, require_auth

logger = logging.getLogger(__name__)

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


# ─────────────────────────────────────────────────────────────────────────────────
# POST /api/ai/generate-preview
# OWNER: Backend Member 1 (Naveen — T1)
# Auth: Optional (works for guest via session_id, or logged-in user via JWT)
# ─────────────────────────────────────────────────────────────────────────────────
@ai_bp.route("/generate-preview", methods=["POST"])
@optional_auth
def generate_preview_route():
    """
    Generate an AI preview image for a custom product configuration.

    Body (JSON):
        category_id         (str, required)
        product_id          (str, optional)
        selected_attributes (dict, required)
        session_id          (str, required — set by frontend on first visit)

    Auth: optional JWT. If present, user_id is extracted from the token.

    Success 200:
        {
            "success": true,
            "data": {
                "output_image_url": "...",
                "from_cache": false,
                "generation_id": "...",
                "disclaimer": "AI-generated approximation — final product may vary."
            }
        }

    Errors: 400 (invalid attrs), 429 (rate limit), 502 (provider error), 504 (timeout)
    """
    body: dict = request.get_json(silent=True) or {}

    # ── Request validation ─────────────────────────────────────────────────────────
    category_id: str = body.get("category_id", "").strip()
    session_id: str = body.get("session_id", "").strip()
    selected_attributes: dict = body.get("selected_attributes", {})

    if not category_id:
        return _error(400, "category_id is required.")
    if not session_id:
        return _error(400, "session_id is required.")
    if not isinstance(selected_attributes, dict):
        return _error(400, "selected_attributes must be a JSON object.")

    product_id: str | None = body.get("product_id") or None
    input_reference_image: str | None = body.get("input_reference_image") or None

    # Extract user_id from JWT (set by @optional_auth decorator, or None for guest).
    user_id: str | None = getattr(g, "user_id", None)

    # ── Orchestrate ────────────────────────────────────────────────────────────────
    result = generate_preview(
        category_id=category_id,
        product_id=product_id,
        selected_attributes=selected_attributes,
        session_id=session_id,
        user_id=user_id,
        input_reference_image=input_reference_image,
    )

    # ── Build response per spec §9 ─────────────────────────────────────────────────
    if result.success:
        return jsonify({
            "success": True,
            "data": {
                "output_image_url": result.output_image_url,
                "from_cache": result.from_cache,
                "generation_id": result.generation_id,
                "disclaimer": result.disclaimer,
            },
        }), 200

    # Error responses — never leak raw provider details to the client.
    if result.error_code == 429:
        return jsonify({
            "success": False,
            "message": result.error_message,
            "data": {
                "limit_reached": result.limit_reached,
                "limit_scope": result.limit_scope,
            },
        }), 429

    if result.error_code == 504:
        return jsonify({
            "success": False,
            "message": result.error_message,
        }), 504

    # 400 or 502
    return jsonify({
        "success": False,
        "message": result.error_message,
    }), result.error_code or 500


# ─────────────────────────────────────────────────────────────────────────────────
# GET /api/ai/generations/<user_id>
# OWNER: Backend Member 2 (Gokul — T4)
# Fully implemented history retrieval endpoint with proper authorization checks.
# ─────────────────────────────────────────────────────────────────────────────────
@ai_bp.route("/generations/<string:user_id>", methods=["GET"])
@require_auth
def get_user_generations_route(user_id: str):
    """
    Return a user's AI generation history (most recent first, paginated).
    Auth required. Must match the requesting user's ID (or admin).

    Query params:
        page     (int, default 1)
        per_page (int, default 20)

    Success 200:
        {
            "success": true,
            "data": {
                "generations": [...],
                "total": 100,
                "page": 1,
                "per_page": 20
            }
        }
    """
    # Verify the requesting user can only see their own history (or admin bypass).
    requesting_user_id: str | None = getattr(g, "user_id", None)
    is_admin: bool = getattr(g, "is_admin", False)

    if not is_admin and requesting_user_id != user_id:
        return _error(403, "You can only view your own generation history.")

    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(100, max(1, int(request.args.get("per_page", 20))))
    except (ValueError, TypeError):
        page, per_page = 1, 20

    generations = get_user_generations(user_id, page=page, per_page=per_page)
    total = count_user_generations(user_id)

    return jsonify({
        "success": True,
        "data": {
            "generations": generations,
            "total": total,
            "page": page,
            "per_page": per_page,
        },
    }), 200


# ─── Shared error helper ──────────────────────────────────────────────────────────
def _error(code: int, message: str):
    return jsonify({"success": False, "message": message}), code
>>>>>>> origin/main
