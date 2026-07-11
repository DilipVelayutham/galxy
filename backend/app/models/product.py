"""
app/models/product.py — Products collection schema, index definitions,
and projection helpers.

Owned by: Module 3
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo import ASCENDING, TEXT
from pymongo.database import Database

# ── Constants ───────────────────────────────────────────────────────────

COLLECTION = "products"

def get_product(product_id):
    """
    Retrieves a product document by its ObjectId.
    """
    from app.db import get_db
    from bson import ObjectId
    from bson.errors import InvalidId
    db = get_db()
    try:
        p_id = ObjectId(product_id) if isinstance(product_id, str) else product_id
    except (InvalidId, TypeError, Exception):
        return None
    return db.products.find_one({"_id": p_id})

def is_product_active(product):
    """
    Checks if a product is active and not soft-deleted.
    """
    if not product:
        return False
    active = product.get("active", product.get("is_active", True))
    is_deleted = product.get("is_deleted", False)
    return active and not is_deleted


VALID_TYPES = {"pre_designed", "fully_custom"}
VALID_STOCK_STATUSES = {"in_stock", "made_to_order", "out_of_stock"}
VALID_SORT_OPTIONS = {"newest", "price_asc", "price_desc", "popular"}

# Fields returned in list responses (lightweight — no images[], specifications,
# default_attributes).  Applied as a MongoDB projection.
LIST_PROJECTION: dict[str, int] = {
    "_id": 1,
    "title": 1,
    "slug": 1,
    "category_slug": 1,
    "thumbnail": 1,
    "base_price": 1,
    "stock_status": 1,
    "rating_avg": 1,
    "is_featured": 1,
}


# ── Default document factory ───────────────────────────────────────────────────

def default_product() -> dict[str, Any]:
    """
    Return a new product document populated with safe defaults.
    Callers must supply: category_id, category_slug, title, slug, type,
    base_price, and (optionally) images, thumbnail, description,
    specifications, default_attributes, tags.
    """
    now = utcnow()
    return {
        # Identity
        "category_id": None,           # ObjectId — required
        "category_slug": "",           # denormalized copy — required
        "title": "",                   # required
        "slug": "",                    # required, unique
        "type": "pre_designed",        # "pre_designed" | "fully_custom"
        # Pricing & media
        "base_price": 0,
        "images": [],
        "thumbnail": "",
        "description": "",
        # Structured data
        "specifications": {
            # e.g. {"material": "Flex LED Neon", "power": "12V Adapter", …}
        },
        "default_attributes": {},      # pre_designed: filled; fully_custom: {}
        # Fulfilment
        "stock_status": "in_stock",    # "in_stock" | "made_to_order" | "out_of_stock"
        # Discovery
        "tags": [],
        "is_featured": False,
        "is_active": True,
        # Analytics
        "views": 0,
        "rating_avg": 0.0,
        "rating_count": 0,
        # Timestamps
        "created_at": now,
        "updated_at": now,
    }


# ── Index creation (idempotent) ────────────────────────────────────────────────

def create_indexes(db: Database) -> None:
    """
    Create all required indexes on the products collection.
    Safe to call multiple times — MongoDB ignores duplicate index requests.

    Index list
    ----------
    1. slug        — unique (primary lookup key)
    2. category_id — equality filter
    3. is_active   — filter (nearly every query)
    4. is_featured — filter
    5. tags        — multikey filter (matches any tag in the array)
    6. Text index  — full-text search on title + description + tags
    """
    col = db[COLLECTION]

    col.create_index([("slug", ASCENDING)], unique=True, name="slug_unique")
    col.create_index([("category_id", ASCENDING)], name="category_id_filter")
    col.create_index([("is_active", ASCENDING)], name="is_active_filter")
    col.create_index([("is_featured", ASCENDING)], name="is_featured_filter")
    col.create_index([("tags", ASCENDING)], name="tags_filter")
    
    # Text index — full-text search on title + description + tags
    try:
        col.create_index(
            [("title", TEXT), ("description", TEXT), ("tags", TEXT)],
            name="text_search",
            default_language="english",
        )
    except Exception:
        # If the index structure has changed (e.g. from title + description to include tags),
        # drop the old index and recreate it.
        try:
            col.drop_index("text_search")
            col.create_index(
                [("title", TEXT), ("description", TEXT), ("tags", TEXT)],
                name="text_search",
                default_language="english",
            )
        except Exception as e:
            import warnings
            warnings.warn(
                f"Failed to recreate text index 'text_search' (needed for title + description + tags): {e}",
                RuntimeWarning,
                stacklevel=2,
            )


# ── Projection / serialization helpers ────────────────────────────────────────

def to_list_view(doc: dict[str, Any]) -> dict[str, Any]:
    """
    Strip heavy fields and convert ObjectIds to strings.
    Used by list + search responses.
    """
    return {
        "_id": str(doc["_id"]),
        "title": doc.get("title", ""),
        "slug": doc.get("slug", ""),
        "category_slug": doc.get("category_slug", ""),
        "thumbnail": doc.get("thumbnail", ""),
        "base_price": doc.get("base_price", 0),
        "stock_status": doc.get("stock_status", "in_stock"),
        "rating_avg": doc.get("rating_avg", 0.0),
        "is_featured": doc.get("is_featured", False),
    }


def to_detail_view(doc: dict[str, Any], category: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Return the full product document with ObjectIds serialized.
    Optionally embeds the owning category inline under the "category" key.
    """
    result: dict[str, Any] = {
        "_id": str(doc["_id"]),
        "category_id": str(doc["category_id"]) if doc.get("category_id") else None,
        "category_slug": doc.get("category_slug", ""),
        "title": doc.get("title", ""),
        "slug": doc.get("slug", ""),
        "type": doc.get("type", "pre_designed"),
        "base_price": doc.get("base_price", 0),
        "images": doc.get("images", []),
        "thumbnail": doc.get("thumbnail", ""),
        "description": doc.get("description", ""),
        "specifications": doc.get("specifications", {}),
        "default_attributes": doc.get("default_attributes", {}),
        "stock_status": doc.get("stock_status", "in_stock"),
        "tags": doc.get("tags", []),
        "is_featured": doc.get("is_featured", False),
        "is_active": doc.get("is_active", True),
        "views": doc.get("views", 0),
        "rating_avg": doc.get("rating_avg", 0.0),
        "rating_count": doc.get("rating_count", 0),
        "created_at": _iso(doc.get("created_at")),
        "updated_at": _iso(doc.get("updated_at")),
    }

    if category is not None:
        result["category"] = {
            "_id": str(category["_id"]) if category.get("_id") else None,
            "slug": category.get("slug", ""),
            "name": category.get("name", ""),
            "attribute_schema": category.get("attribute_schema", {}),
            "accent_color": category.get("accent_color", ""),
        }

    return result


# ── Validation helpers ───────────────────────────────────────────────────────

def validate_product_payload(data: dict[str, Any], *, is_update: bool = False) -> list[str]:
    """
    Validate incoming product data.  Returns a list of error strings.
    Pass is_update=True to skip required-field checks (partial updates allowed).
    """
    errors: list[str] = []

    if not is_update:
        # Note: 'slug' is intentionally omitted — create_product() auto-generates
        # a unique slug from the title when none is provided.
        for required in ("category_id", "title", "type", "base_price"):
            if not data.get(required):
                errors.append(f"'{required}' is required.")

    if "category_id" in data and data["category_id"]:
        val = data["category_id"]
        if not (isinstance(val, (str, ObjectId)) and ObjectId.is_valid(str(val))):
            errors.append("'category_id' must be a valid 24-character hex ObjectId string.")

    if "type" in data and data["type"] not in VALID_TYPES:
        errors.append(f"'type' must be one of {sorted(VALID_TYPES)}.")

    if "stock_status" in data and data["stock_status"] not in VALID_STOCK_STATUSES:
        errors.append(f"'stock_status' must be one of {sorted(VALID_STOCK_STATUSES)}.")

    if "base_price" in data:
        try:
            if float(data["base_price"]) < 0:
                errors.append("'base_price' must be >= 0.")
        except (TypeError, ValueError):
            errors.append("'base_price' must be a number.")

    return errors


# ── Private helpers ────────────────────────────────────────────────────────

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()
