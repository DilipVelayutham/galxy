"""
app/services/order_service.py

Owns checkout(), get(), and list() — the customer-facing order
operations, plus two small helpers exposed for other modules to import
(has_delivered_order_for_product for Module 9, get_order_by_id for
Stream B's order_status_service.py).

Do NOT add status-transition or admin logic here — that's Stream B's
file (order_status_service.py). If you find yourself editing that file
instead of this one, stop and check with Stream B first.

Cross-module dependencies below are called, never re-implemented — see
"What You Do NOT Do" in the spec. Adjust the import paths to match this
project's actual module layout; the function signatures are what matter.
"""

import logging
from typing import Any, Dict, List, Optional

from bson import ObjectId
from pymongo.database import Database

from app.models.order import (
    ORDERS_COLLECTION,
    CustomerSnapshot,
    OrderItem,
    build_order_document,
    strip_admin_fields,
    to_list_item,
)
from app.services.order_number_service import generate_order_number

# --- Cross-module dependencies (called, never duplicated here) -----------
from app.services.address_service import get_address_for_checkout
from app.services.configurator_service import validate_attributes_by_id as validate_attributes
from app.services.pricing_service import calculate_price_by_id as calculate_price
from app.services.cart_service import clear_cart, get_cart
from app.services.notification_service import trigger_notification

logger = logging.getLogger(__name__)


class CheckoutError(Exception):
    """Raised for every checkout 400 — empty cart, no address, or item
    problems. item_errors is empty for the first two; populated for the
    third, matching the API contract's data.errors shape.
    """

    def __init__(self, message: str, item_errors: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message)
        self.message = message
        self.item_errors = item_errors or []


class OrderNotFoundError(Exception):
    """Raised for both 'doesn't exist' and 'belongs to someone else'. The
    route layer must map this to 404 in BOTH cases, never 403 — see the
    order-number enumeration note in Section 6.
    """


def _price_and_validate_items(cart_items: List[Dict[str, Any]]) -> List[OrderItem]:
    """Re-run validate_attributes(), is_active checks, and
    calculate_price() fresh for every cart item. Returns the priced items
    ready to write onto the order, or raises CheckoutError listing every
    item that failed — stale attributes, deactivation, or a price change
    the customer hasn't confirmed. This never partially checks out: any
    item_errors means the whole checkout is rejected (flag, don't drop).
    """
    priced_items: List[OrderItem] = []
    item_errors: List[Dict[str, Any]] = []

    for cart_item in cart_items:
        product_id = cart_item["product_id"]
        category_id = cart_item["category_id"]
        product_title = cart_item.get("product_title")

        # is_active re-check first — no point validating/pricing something
        # that's been pulled from the catalog since it was added.
        if not cart_item.get("product_is_active", True) or not cart_item.get(
            "category_is_active", True
        ):
            item_errors.append(
                {
                    "product_id": product_id,
                    "product_title": product_title,
                    "code": "deactivated",
                    "reason": "This item is no longer available.",
                }
            )
            continue

        validation = validate_attributes(
            category_id=category_id,
            selected_attributes=cart_item.get("selected_attributes", {}),
        )
        if not validation.get("valid", False):
            item_errors.append(
                {
                    "product_id": product_id,
                    "product_title": product_title,
                    "code": "stale_attributes",
                    "reason": validation.get(
                        "reason", "This item's options are no longer valid."
                    ),
                }
            )
            continue

        pricing = calculate_price(
            product_id=product_id,
            category_id=category_id,
            selected_attributes=cart_item.get("selected_attributes", {}),
            quantity=cart_item.get("quantity", 1),
        )
        unit_price = pricing["unit_price"]
        line_total = pricing["line_total"]

        # The cart's stored estimate is never reused as-is — but if it
        # disagrees with the freshly calculated price, the customer needs
        # to see and confirm that before a real order is written.
        stored_estimate = cart_item.get("unit_price_estimate")
        if stored_estimate is not None and stored_estimate != unit_price:
            item_errors.append(
                {
                    "product_id": product_id,
                    "product_title": product_title,
                    "code": "price_changed",
                    "reason": "The price for this item has changed.",
                }
            )
            continue

        priced_items.append(
            {
                "product_id": product_id,
                "product_title": product_title,
                "category_id": category_id,
                "category_name": cart_item.get("category_name"),
                "selected_attributes": cart_item.get("selected_attributes", {}),
                "quantity": cart_item.get("quantity", 1),
                "unit_price_estimate": unit_price,
                "line_total_estimate": line_total,
                "price_breakdown": pricing.get("breakdown", []),
                "ai_preview_image": cart_item.get("ai_preview_image"),
                "reference_image": cart_item.get("reference_image"),
                "custom_text": cart_item.get("custom_text"),
            }
        )

    if item_errors:
        raise CheckoutError(
            "Some items in your cart need attention before you can check out.",
            item_errors=item_errors,
        )

    return priced_items


def checkout(db: Database, *, user_id: Any, address_id: Optional[str] = None) -> Dict[str, Any]:
    """The single most important write path in the platform — the final
    gate before something becomes a real business commitment for Asil.
    Every step here is a required defensive check (Section 5).
    """
    cart = get_cart(user_id=user_id)
    cart_items = cart.get("items", [])

    if not cart_items:
        raise CheckoutError("Cart is empty")

    priced_items = _price_and_validate_items(cart_items)

    address = get_address_for_checkout(user_id=user_id, address_id=address_id)
    if not address:
        raise CheckoutError("No address available")

    customer_snapshot: CustomerSnapshot = {
        "name": address["customer_name"],
        "phone": address["customer_phone"],
        "email": address["customer_email"],
        "address": {
            "line1": address["line1"],
            "line2": address.get("line2"),
            "city": address["city"],
            "state": address["state"],
            "pincode": address["pincode"],
        },
    }

    estimated_total = sum(item.get("line_total_estimate", 0) for item in priced_items)
    order_number = generate_order_number(db)

    order_doc = build_order_document(
        order_number=order_number,
        user_id=user_id,
        customer_snapshot=customer_snapshot,
        items=priced_items,
        estimated_total=estimated_total,
    )

    # Step 6: insert. If this raises, nothing downstream runs — no cart
    # clear, no notification. Let the exception propagate to the route.
    db[ORDERS_COLLECTION].insert_one(order_doc)

    # Step 7: clear cart — best-effort. A failure here must NOT fail the
    # response: the order already exists and is real; a stale cart is a
    # minor cleanup issue to log and fix out of band, not a checkout error.
    try:
        clear_cart(user_id=user_id)
    except Exception:
        logger.exception(
            "Order %s created but cart clear failed for user %s",
            order_number,
            user_id,
        )

    # Step 8: notify — same best-effort posture as cart-clear.
    try:
        trigger_notification(
            event="order_created",
            user_id=user_id,
            order_number=order_number,
            status=order_doc["status"],
            note=f"Order {order_number} received",
        )
    except Exception:
        logger.exception(
            "Order %s created but order_created notification failed for user %s",
            order_number,
            user_id,
        )

    return strip_admin_fields(order_doc)


def get(db: Database, *, user_id: Any, order_number: str) -> Dict[str, Any]:
    """GET /api/orders/:order_number. Raises OrderNotFoundError for both a
    nonexistent order_number and one owned by someone else — the route
    layer must return 404 for both, never 403.
    """
    order_doc = db[ORDERS_COLLECTION].find_one(
        {"order_number": order_number, "user_id": user_id}
    )
    if not order_doc:
        raise OrderNotFoundError(order_number)

    return strip_admin_fields(order_doc)


def list(db: Database, *, user_id: Any, page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """GET /api/orders. Lightweight rows only — no items[], no
    status_history — per Section 6.
    """
    page = max(page, 1)
    limit = max(1, min(limit, 50))
    skip = (page - 1) * limit

    query = {"user_id": user_id}
    total = db[ORDERS_COLLECTION].count_documents(query)

    cursor = (
        db[ORDERS_COLLECTION]
        .find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    rows = [to_list_item(doc) for doc in cursor]
    total_pages = (total + limit - 1) // limit if total else 0

    return {
        "data": rows,
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
    }


def has_delivered_order_for_product(db: Database, *, user_id: Any, product_id: str) -> bool:
    """Module 9 (Reviews) helper — gates review submission on a delivered
    order containing this product, per the Handoff Contract, so Module 9
    doesn't need to duplicate order-querying logic.
    """
    match = db[ORDERS_COLLECTION].find_one(
        {"user_id": user_id, "status": "delivered", "items.product_id": product_id},
        {"_id": 1},
    )
    return match is not None


def get_order_by_id(db: Database, *, order_id: ObjectId) -> Optional[Dict[str, Any]]:
    """Shared lookup for Stream B's order_status_service.py (Section 9
    addendum) — keep it here since this file owns the query logic.
    Returns the RAW document, including admin_notes: this is an internal
    helper for Stream B's writes, not a customer-facing response, so it
    does not call strip_admin_fields().
    """
    return db[ORDERS_COLLECTION].find_one({"_id": order_id})
