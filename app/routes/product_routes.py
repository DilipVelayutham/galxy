"""
app/routes/product_routes.py — Public API routes for the products domain.

Owned by: Module 3

Endpoints
---------
GET  /api/products                 — filtered + sorted list (lightweight)
GET  /api/products/search          — full-text search (lightweight)
GET  /api/products/<slug>          — full detail + embedded category

Internal / admin endpoints (not part of the public storefront API):
POST   /api/products               — create product
PUT    /api/products/<slug>        — update product
DELETE /api/products/<slug>        — soft-delete product
POST   /api/products/<slug>/images — upload image to Cloudinary
DELETE /api/products/<slug>/images — delete image from Cloudinary
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.db import get_db
from app.services.product_image_service import (
    delete_image,
    extract_public_id,
    upload_image,
    upload_thumbnail,
)
from app.services.product_service import (
    create_product,
    delete_product,
    get_product_by_slug,
    list_products,
    search_products,
    update_product,
)

product_bp = Blueprint("products", __name__, url_prefix="/api/products")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_int(value: str | None, default: int) -> int:
    try:
        return max(1, int(value)) if value is not None else default
    except (TypeError, ValueError):
        return default


def _parse_float(value: str | None) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.lower() in ("true", "1", "yes")


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC STOREFRONT ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@product_bp.get("")
def api_list_products():
    """
    GET /api/products
    -----------------
    Query params:
      category    — category slug (exact match)
      min_price   — inclusive lower bound on base_price
      max_price   — inclusive upper bound on base_price
      tags        — comma-separated tag strings (matches any)
      featured    — "true" | "false"
      sort        — newest | price_asc | price_desc | popular
      page        — page number (default 1)
      limit       — page size   (default 20)

    200 OK — lightweight list response
    """
    db = get_db()

    category = request.args.get("category") or None
    min_price = _parse_float(request.args.get("min_price"))
    max_price = _parse_float(request.args.get("max_price"))
    tags_raw = request.args.get("tags")
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else None
    featured = _parse_bool(request.args.get("featured"))
    sort = request.args.get("sort") or None
    page = _parse_int(request.args.get("page"), 1)
    limit = _parse_int(request.args.get("limit"), 20)

    result = list_products(
        db,
        category=category,
        min_price=min_price,
        max_price=max_price,
        tags=tags,
        featured=featured,
        sort=sort,
        page=page,
        limit=limit,
    )
    return jsonify(result), 200


@product_bp.get("/search")
def api_search_products():
    """
    GET /api/products/search?q=<query>
    ------------------------------------
    Full-text search across title + description + tags.
    Returns 400 if ``q`` is shorter than 2 characters.
    Same lightweight list response shape as GET /api/products.
    """
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify({"success": False, "error": "Search query must be at least 2 characters."}), 400

    db = get_db()
    page = _parse_int(request.args.get("page"), 1)
    limit = _parse_int(request.args.get("limit"), 20)

    result = search_products(q, db, page=page, limit=limit)
    return jsonify(result), 200


@product_bp.get("/<slug>")
def api_get_product(slug: str):
    """
    GET /api/products/<slug>
    ------------------------
    Returns the full product document with the owning category embedded
    inline under ``category`` (fields: _id, slug, name, attribute_schema,
    accent_color).

    Side effect: increments ``views`` by 1 asynchronously.
    Returns 404 if the product does not exist or is inactive.
    """
    db = get_db()
    product = get_product_by_slug(slug, db)
    if product is None:
        return jsonify({"success": False, "error": "Product not found."}), 404

    return jsonify({"success": True, "data": product}), 200


# ══════════════════════════════════════════════════════════════════════════════
# INTERNAL / ADMIN ROUTES
# (Not consumed by the storefront — used by the admin panel / seeder scripts)
# ══════════════════════════════════════════════════════════════════════════════

@product_bp.post("")
def api_create_product():
    """
    POST /api/products
    ------------------
    Body: JSON matching the product schema.
    Returns 201 with the full product document on success.
    Returns 400 with validation errors on failure.
    """
    db = get_db()
    data = request.get_json(silent=True) or {}
    doc, errors = create_product(data, db)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400
    return jsonify({"success": True, "data": doc}), 201


@product_bp.put("/<slug>")
def api_update_product(slug: str):
    """
    PUT /api/products/<slug>
    -------------------------
    Partial update. Only fields present in the JSON body are changed.
    Returns 200 with the updated full document.
    Returns 400/404 on error.
    """
    db = get_db()
    data = request.get_json(silent=True) or {}
    doc, errors = update_product(slug, data, db)
    if errors:
        status = 404 if "not found" in (errors[0] if errors else "").lower() else 400
        return jsonify({"success": False, "errors": errors}), status
    return jsonify({"success": True, "data": doc}), 200


@product_bp.delete("/<slug>")
def api_delete_product(slug: str):
    """
    DELETE /api/products/<slug>
    ---------------------------
    Soft-delete (sets is_active = False).
    Returns 200 on success, 404 if not found.
    """
    db = get_db()
    deleted = delete_product(slug, db)
    if not deleted:
        return jsonify({"success": False, "error": "Product not found."}), 404
    return jsonify({"success": True, "message": "Product deactivated."}), 200


# ── Image management routes ────────────────────────────────────────────────────

@product_bp.post("/<slug>/images")
def api_upload_image(slug: str):
    """
    POST /api/products/<slug>/images
    ---------------------------------
    Multipart form upload. Fields:
      file        — image file (required)
      is_thumbnail — "true" | "false" (optional, default false)

    Returns the Cloudinary secure_url and public_id.
    On success, caller should PATCH the product's images[] / thumbnail via
    PUT /api/products/<slug>.
    """
    db = get_db()
    product = get_product_by_slug(slug, db)
    if product is None:
        return jsonify({"success": False, "error": "Product not found."}), 404

    file = request.files.get("file")
    if file is None:
        return jsonify({"success": False, "error": "No file provided."}), 400

    is_thumb = _parse_bool(request.form.get("is_thumbnail")) or False

    try:
        if is_thumb:
            url, public_id = upload_thumbnail(file, folder=f"products/{slug}/thumbnails")
        else:
            url, public_id = upload_image(file, folder=f"products/{slug}")
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500

    return jsonify({"success": True, "secure_url": url, "public_id": public_id}), 201


@product_bp.delete("/<slug>/images")
def api_delete_image(slug: str):
    """
    DELETE /api/products/<slug>/images
    ------------------------------------
    JSON body: { "public_id": "products/slug/abc123" }
               OR
               { "url": "https://res.cloudinary.com/..." }

    Deletes the asset from Cloudinary.
    """
    db = get_db()
    product = get_product_by_slug(slug, db)
    if product is None:
        return jsonify({"success": False, "error": "Product not found."}), 404

    body = request.get_json(silent=True) or {}
    public_id: str | None = body.get("public_id")

    if not public_id and body.get("url"):
        public_id = extract_public_id(body["url"])

    if not public_id:
        return jsonify({"success": False, "error": "'public_id' or 'url' is required."}), 400

    deleted = delete_image(public_id)
    if not deleted:
        return jsonify({"success": False, "error": "Could not delete asset from Cloudinary."}), 500

    return jsonify({"success": True, "message": "Image deleted from Cloudinary."}), 200
