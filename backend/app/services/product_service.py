"""
app/services/product_service.py — Core CRUD, search, filtering, and
pagination logic for the products collection.

Owned by: Module 3

Design notes
------------
- All public functions accept an explicit ``db`` parameter so they are
  easily testable without Flask's application context.
- View increments are fire-and-forget (background thread) so they never
  block the HTTP response.
- ``get_product_by_slug`` fetches the owning category document from the
  ``categories`` collection and embeds it inline.  If the categories
  collection does not yet exist (Module 2 not deployed), the embed is
  silently omitted.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from pymongo.database import Database

from app.models.product import (
    COLLECTION,
    LIST_PROJECTION,
    default_product,
    to_detail_view,
    to_list_view,
    validate_product_payload,
)
from app.utils.search_helper import (
    build_filter_query,
    build_sort_spec,
    build_text_search_query,
    calc_pagination,
)
from app.utils.slug_helper import ensure_unique_slug, generate_slug


# ── Helpers ───────────────────────────────────────────────────────────

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _fetch_category(db: Database, category_id: Any) -> dict[str, Any] | None:
    """
    Fetch the owning category from the ``categories`` collection.
    Returns None silently if the collection doesn't exist or no match found.

    # FLAG: Module 2 dependency — categories collection must exist.
    """
    try:
        if isinstance(category_id, str):
            category_id = ObjectId(category_id)
        return db["categories"].find_one(
            {"_id": category_id},
            {"_id": 1, "slug": 1, "name": 1, "attribute_schema": 1, "accent_color": 1},
        )
    except Exception:
        return None


def _increment_views_async(db: Database, product_id: ObjectId) -> None:
    """
    Increment the views counter in a background thread.
    Fire-and-forget — never blocks the HTTP response.
    """
    def _run():
        try:
            db[COLLECTION].update_one(
                {"_id": product_id},
                {"$inc": {"views": 1}},
            )
        except Exception:
            pass  # silently ignore; views are non-critical analytics

    threading.Thread(target=_run, daemon=True).start()


# ── CRUD ────────────────────────────────────────────────────────────

def create_product(data: dict[str, Any], db: Database) -> tuple[dict[str, Any] | None, list[str]]:
    """
    Validate and insert a new product document.

    Returns
    -------
    (inserted_doc, errors)
        ``errors`` is an empty list on success.
    """
    errors = validate_product_payload(data)
    if errors:
        return None, errors

    doc = default_product()
    doc.update(
        {
            "category_id": ObjectId(data["category_id"]),
            "category_slug": data.get("category_slug", ""),
            "title": data["title"].strip(),
            "type": data["type"],
            "base_price": float(data["base_price"]),
            "images": data.get("images", []),
            "thumbnail": data.get("thumbnail", ""),
            "description": data.get("description", ""),
            "specifications": data.get("specifications", {}),
            "default_attributes": data.get("default_attributes", {}),
            "stock_status": data.get("stock_status", "in_stock"),
            "tags": data.get("tags", []),
            "is_featured": bool(data.get("is_featured", False)),
            "is_active": bool(data.get("is_active", True)),
        }
    )

    # Generate a unique slug from the title (or use a caller-supplied one)
    base_slug = data.get("slug") or generate_slug(data["title"])
    doc["slug"] = ensure_unique_slug(base_slug, db[COLLECTION])

    result = db[COLLECTION].insert_one(doc)
    doc["_id"] = result.inserted_id
    return to_detail_view(doc), []


def get_product_by_slug(slug: str, db: Database) -> dict[str, Any] | None:
    """
    Fetch a single active product by slug.

    Side effects
    ------------
    - Increments ``views`` asynchronously (fire-and-forget).
    - Embeds the owning category document inline under ``category``.

    Returns None if the product does not exist or is inactive.
    """
    doc = db[COLLECTION].find_one({"slug": slug, "is_active": True})
    if doc is None:
        return None

    # Fire-and-forget view increment (does not block response)
    _increment_views_async(db, doc["_id"])

    # Fetch and embed the category (Module 2 dependency — gracefully degrades)
    category = _fetch_category(db, doc.get("category_id"))

    return to_detail_view(doc, category=category)


def update_product(
    slug: str,
    data: dict[str, Any],
    db: Database,
) -> tuple[dict[str, Any] | None, list[str]]:
    """
    Partially update an existing product identified by *slug*.

    Only fields present in *data* are changed.  ``updated_at`` is always
    refreshed.  Slug regeneration happens if ``title`` changes and no
    explicit ``slug`` is provided.

    Returns
    -------
    (updated_doc, errors)
    """
    errors = validate_product_payload(data, is_update=True)
    if errors:
        return None, errors

    existing = db[COLLECTION].find_one({"slug": slug, "is_active": True})
    if existing is None:
        return None, ["Product not found."]

    # Build the $set payload
    set_payload: dict[str, Any] = {"updated_at": _utcnow()}

    _str_fields = ("category_slug", "title", "thumbnail", "description", "type", "stock_status")
    _dict_fields = ("specifications", "default_attributes")
    _list_fields = ("images", "tags")
    _bool_fields = ("is_featured", "is_active")

    for field in _str_fields:
        if field in data:
            set_payload[field] = data[field]

    for field in _dict_fields:
        if field in data:
            set_payload[field] = data[field]

    for field in _list_fields:
        if field in data:
            set_payload[field] = data[field]

    for field in _bool_fields:
        if field in data:
            set_payload[field] = bool(data[field])

    if "base_price" in data:
        set_payload["base_price"] = float(data["base_price"])

    if "category_id" in data:
        set_payload["category_id"] = ObjectId(data["category_id"])

    # Slug update: explicit > derived from new title > keep existing
    if "slug" in data:
        new_slug = ensure_unique_slug(data["slug"], db[COLLECTION], exclude_id=existing["_id"])
        set_payload["slug"] = new_slug
    elif "title" in data:
        new_slug = ensure_unique_slug(
            generate_slug(data["title"]), db[COLLECTION], exclude_id=existing["_id"]
        )
        set_payload["slug"] = new_slug

    db[COLLECTION].update_one({"_id": existing["_id"]}, {"$set": set_payload})
    updated = db[COLLECTION].find_one({"_id": existing["_id"]})
    category = _fetch_category(db, updated.get("category_id"))
    return to_detail_view(updated, category=category), []


def delete_product(slug: str, db: Database) -> bool:
    """
    Soft-delete a product by setting ``is_active = False``.

    Returns True if a document was matched and updated, False otherwise.
    """
    result = db[COLLECTION].update_one(
        {"slug": slug, "is_active": True},
        {"$set": {"is_active": False, "updated_at": _utcnow()}},
    )
    return result.matched_count > 0


# ── Listing (filter + sort + paginate) ────────────────────────────────────────

def list_products(
    db: Database,
    *,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    tags: Optional[list[str]] = None,
    featured: Optional[bool] = None,
    sort: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Return a paginated, filtered, sorted list of active products.

    Response shape matches the public API spec (lightweight list view).
    """
    query = build_filter_query(
        category=category,
        min_price=min_price,
        max_price=max_price,
        tags=tags,
        featured=featured,
    )
    sort_spec = build_sort_spec(sort)

    col = db[COLLECTION]
    total = col.count_documents(query)

    skip = (max(1, page) - 1) * max(1, limit)
    cursor = col.find(query, LIST_PROJECTION).sort(sort_spec).skip(skip).limit(limit)

    data = [to_list_view(doc) for doc in cursor]
    pagination = calc_pagination(page, limit, total)

    return {"success": True, "data": data, **pagination}


# ── Search ───────────────────────────────────────────────────────────

def search_products(
    q: str,
    db: Database,
    *,
    page: int = 1,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Full-text search across ``title`` + ``description`` + ``tags``.

    Requires the text index created by ``app.models.product.create_indexes``.
    Results are ordered by MongoDB text-score relevance descending.

    Returns the same lightweight list shape as ``list_products``.
    """
    query = build_text_search_query(q)
    col = db[COLLECTION]
    total = col.count_documents(query)

    skip = (max(1, page) - 1) * max(1, limit)
    cursor = (
        col.find(query, {**LIST_PROJECTION, "score": {"$meta": "textScore"}})
        .sort([("score", {"$meta": "textScore"})])
        .skip(skip)
        .limit(limit)
    )

    data = [to_list_view(doc) for doc in cursor]
    pagination = calc_pagination(page, limit, total)

    return {"success": True, "data": data, **pagination}

class ProductService:
    @staticmethod
    def get_products(params, include_inactive=True):
        from app.db import get_db
        db = get_db()
        # Parse query params
        category = params.get("category")
        min_price = params.get("min_price")
        if min_price is not None and str(min_price).strip():
            min_price = float(min_price)
        max_price = params.get("max_price")
        if max_price is not None and str(max_price).strip():
            max_price = float(max_price)
        tags = params.getlist("tags") if hasattr(params, "getlist") else params.get("tags")
        if isinstance(tags, str):
            tags = [tags]
        featured = params.get("featured")
        if featured is not None and str(featured).strip():
            featured = str(featured).lower() in ("true", "1")
        
        sort = params.get("sort")
        page = int(params.get("page", 1))
        limit = int(params.get("limit", 20))
        
        # We call the module-level list_products
        res = list_products(
            db,
            category=category,
            min_price=min_price,
            max_price=max_price,
            tags=tags,
            featured=featured,
            sort=sort,
            page=page,
            limit=limit
        )
        return res["data"], res["page"], res["limit"], res["total"]

    @staticmethod
    def create_product(validated_data):
        from app.db import get_db
        db = get_db()
        product, errors = create_product(validated_data, db)
        if errors:
            raise ValueError(", ".join(errors))
        return product

    @staticmethod
    def update_product(product_id, validated_data):
        from app.db import get_db
        from bson import ObjectId
        db = get_db()
        # Resolve product ID or slug to the document
        try:
            p_id = ObjectId(product_id)
            prod = db.products.find_one({"_id": p_id})
        except Exception:
            prod = db.products.find_one({"slug": product_id})
            
        if not prod:
            return None
        product, errors = update_product(prod["slug"], validated_data, db)
        if errors:
            raise ValueError(", ".join(errors))
        return product

    @staticmethod
    def soft_delete_product(product_id):
        from app.db import get_db
        from bson import ObjectId
        db = get_db()
        try:
            p_id = ObjectId(product_id)
            prod = db.products.find_one({"_id": p_id})
        except Exception:
            prod = db.products.find_one({"slug": product_id})
            
        if not prod:
            return None
        success = delete_product(prod["slug"], db)
        if not success:
            return None
        return db.products.find_one({"_id": prod["_id"]})

    @staticmethod
    def set_thumbnail(product_id, image_url):
        from app.db import get_db
        from bson import ObjectId
        db = get_db()
        try:
            p_id = ObjectId(product_id)
        except Exception:
            # Fallback if slug passed
            prod = db.products.find_one({"slug": product_id})
            p_id = prod["_id"] if prod else None
            
        if not p_id:
            return None
            
        result = db.products.update_one(
            {"_id": p_id},
            {"$set": {"thumbnail": image_url, "updated_at": _utcnow()}}
        )
        if result.matched_count == 0:
            return None
        # Return fully detailed product
        updated = db.products.find_one({"_id": p_id})
        category = _fetch_category(db, updated.get("category_id"))
        return to_detail_view(updated, category=category)

