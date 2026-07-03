"""
ai_routes.py — Module 5 AI Preview Generation
Flask Blueprint for all AI Preview routes.

ROUTE OWNERSHIP:
  POST /api/ai/generate-preview         ← Backend Member 1 (T1, this file)
  GET  /api/ai/generations/:user_id     ← Backend Member 2 (T4, stub here)

The GET history route is stubbed here with a clear ownership comment so
Backend Member 2 can take it over without a merge conflict on the same file.
Per spec warning (§workflow): agree in advance — consider splitting into
ai_routes.py (POST only) + ai_history_routes.py (GET history/admin) to avoid
Day 3 merge conflicts.
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
# Stub: returns live data from model but final implementation/auth guard is Gokul's.
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
