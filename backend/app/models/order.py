"""
app/models/order.py

Schema reference and light helpers for the `orders` collection. No ODM —
MongoDB documents stay plain dicts — but this module centralizes the
shape so order_service.py, order_status_service.py (Stream B), and the
routes all agree on field names instead of each inventing their own.

Fields written on insert belong to Stream A (this file's caller,
order_service.checkout()). status_history entries after the first,
admin_notes, and final_quoted_price are owned/mutated by Stream B — never
write them here beyond the null/empty defaults below.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict

ORDERS_COLLECTION = "orders"
COUNTERS_COLLECTION = "counters"

STATUS_RECEIVED = "received"

# Fields that must never appear in a customer-facing response.
ADMIN_ONLY_FIELDS = ("admin_notes", "_id")


class Address(TypedDict, total=False):
    line1: str
    line2: Optional[str]
    city: str
    state: str
    pincode: str


class CustomerSnapshot(TypedDict):
    name: str
    phone: str
    email: str
    address: Address


class PriceBreakdownEntry(TypedDict):
    label: str
    amount: float


class OrderItem(TypedDict, total=False):
    product_id: str
    product_title: Optional[str]
    category_id: str
    category_name: Optional[str]
    selected_attributes: Dict[str, Any]
    quantity: int
    unit_price_estimate: float
    line_total_estimate: float
    price_breakdown: List[PriceBreakdownEntry]
    ai_preview_image: Optional[str]
    reference_image: Optional[str]
    custom_text: Optional[str]


class StatusHistoryEntry(TypedDict):
    status: str
    note: Optional[str]
    updated_by: str
    timestamp: datetime


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def build_order_document(
    *,
    order_number: str,
    user_id: Any,
    customer_snapshot: CustomerSnapshot,
    items: List[OrderItem],
    estimated_total: float,
) -> Dict[str, Any]:
    """Assemble the order document for insertion. Called only from
    order_service.checkout() — don't construct this dict inline anywhere
    else, so the shape stays defined in exactly one place.
    """
    timestamp = now_utc()
    return {
        "order_number": order_number,
        "user_id": user_id,
        "customer_snapshot": customer_snapshot,
        "items": items,
        "estimated_total": estimated_total,
        "final_quoted_price": None,  # Stream B only — leave null on insert
        "status": STATUS_RECEIVED,
        "status_history": [
            {
                "status": STATUS_RECEIVED,
                "note": None,
                "updated_by": "system",
                "timestamp": timestamp,
            }
        ],
        "admin_notes": "",  # Stream B only — do not read/write elsewhere
        "customer_visible_note": None,
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def strip_admin_fields(order_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Remove fields that must never reach a customer-facing response.
    Always call this on the way OUT of order_service — never rely on the
    frontend to hide admin_notes.
    """
    return {k: v for k, v in order_doc.items() if k not in ADMIN_ONLY_FIELDS}


def to_list_item(order_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Lightweight shape for GET /api/orders — no items[], no
    status_history, per Section 6 of the spec.
    """
    items = order_doc.get("items", [])
    thumbnail = None
    for item in items:
        thumbnail = item.get("ai_preview_image") or item.get("reference_image")
        if thumbnail:
            break

    return {
        "order_number": order_doc["order_number"],
        "status": order_doc["status"],
        "estimated_total": order_doc["estimated_total"],
        "created_at": order_doc["created_at"],
        "item_count": len(items),
        "thumbnail_preview": thumbnail,
    }


def ensure_indexes(db) -> None:
    """Call once at app startup (e.g. from create_app()). order_number is
    unique-indexed; user_id is indexed for order-history lookups — confirm
    both exist before load testing, per the Part 1 handoff note.
    Also ensure status and created_at indexes for admin page performance.
    """
    db[ORDERS_COLLECTION].create_index("order_number", unique=True)
    db[ORDERS_COLLECTION].create_index("user_id")
    db[ORDERS_COLLECTION].create_index("status")
    db[ORDERS_COLLECTION].create_index("created_at")
