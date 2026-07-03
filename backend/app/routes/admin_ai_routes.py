"""
admin_ai_routes.py — Module 5 AI Preview Generation
Admin-only routes for AI usage analytics.

OWNER: Backend Member 2 (Gokul — T4)
This stub is provided so the app initializes correctly and the route is
registered. Backend Member 2 will implement the full logic.

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
