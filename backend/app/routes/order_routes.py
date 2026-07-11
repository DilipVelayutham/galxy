"""
app/routes/order_routes.py

Customer-facing order routes. All routes require @require_auth. Handlers
stay thin — checkout()/get()/list() live in order_service.py so other
callers (Module 9, tests) can import them directly without going through
HTTP, per the Handoff Contract.

Adjust `from app.extensions import mongo` and `app.middleware.auth` below
to match however this project actually exposes the DB handle and the auth
decorator/current-user accessor — the route logic itself doesn't change.
"""

from flask import Blueprint, g, jsonify, request

from app.extensions import mongo
from app.middleware.auth import require_auth
from app.services import order_service
from app.services.order_service import CheckoutError, OrderNotFoundError

order_routes = Blueprint("orders", __name__, url_prefix="/api/orders")


def _success(data, message=None, status=200):
    body = {"success": True, "data": data}
    if message:
        body["message"] = message
    return jsonify(body), status


def _error(message, status=400, errors=None):
    body = {"success": False, "message": message}
    if errors:
        body["errors"] = errors
    return jsonify(body), status


@order_routes.post("/checkout")
@require_auth
def post_checkout():
    payload = request.get_json(silent=True) or {}
    address_id = payload.get("address_id")

    if address_id is not None and not isinstance(address_id, str):
        return _error("address_id must be a string", status=400)

    try:
        order = order_service.checkout(
            mongo.db, user_id=g.current_user_id, address_id=address_id
        )
    except CheckoutError as e:
        return _error(e.message, status=400, errors=e.item_errors)

    return _success(order, message="Order placed", status=201)


@order_routes.get("")
@require_auth
def get_orders():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
    except (ValueError, TypeError):
        return _error("page and limit must be integers", status=400)

    if page < 1:
        return _error("page must be >= 1", status=400)
    if limit < 1 or limit > 50:
        return _error("limit must be between 1 and 50", status=400)

    result = order_service.list(
        mongo.db, user_id=g.current_user_id, page=page, limit=limit
    )

    return (
        jsonify(
            {
                "success": True,
                "data": result["data"],
                "page": result["page"],
                "limit": result["limit"],
                "total": result["total"],
                "totalPages": result["totalPages"],
            }
        ),
        200,
    )


@order_routes.get("/<order_number>")
@require_auth
def get_order(order_number: str):
    try:
        order = order_service.get(
            mongo.db, user_id=g.current_user_id, order_number=order_number
        )
    except OrderNotFoundError:
        # Always 404 here, never 403 — a wrong-owner order and a
        # nonexistent one must look identical to the caller, to avoid
        # order-number enumeration.
        return _error("Order not found", status=404)

    return _success(order)
