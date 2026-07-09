"""
app/routes/admin_routes.py — Dedicated admin routes to support the React frontend dashboard.
"""

from __future__ import annotations

import time
from typing import Any
from flask import Blueprint, jsonify, request
from bson import ObjectId
from app.db import get_db
from app.services.product_image_service import upload_image, delete_image
from app.models.product import (
    COLLECTION,
    to_detail_view,
    to_list_view,
    validate_product_payload,
    default_product,
    utcnow,
)
from app.utils.slug_helper import ensure_unique_slug, generate_slug

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

# Initial mock categories to auto-seed if categories collection is empty
INITIAL_CATEGORIES = [
    {
        "_id": ObjectId("000000000000000000000001"),
        "name": "Apparel",
        "slug": "apparel",
        "accent_color": "#FF2E8A",
        "hero_image": "https://picsum.photos/seed/cat-apparel/800/400",
        "attribute_schema": [
            { "key": "color", "label": "Color", "type": "select", "options": ["Black", "White", "Burgundy", "Volt Green"] },
            { "key": "size", "label": "Size", "type": "select", "options": ["S", "M", "L", "XL"] },
            { "key": "material", "label": "Material", "type": "text" },
        ],
    },
    {
        "_id": ObjectId("000000000000000000000002"),
        "name": "Electronics Accessories",
        "slug": "electronics-accessories",
        "accent_color": "#6C5CE7",
        "hero_image": "https://picsum.photos/seed/cat-electronics/800/400",
        "attribute_schema": [
            { "key": "color", "label": "Color", "type": "select", "options": ["Midnight Black", "Pearl White", "Titanium Grey"] },
            { "key": "warranty_months", "label": "Warranty (months)", "type": "number" },
            { "key": "battery_life_hrs", "label": "Battery Life (hrs)", "type": "slider", "min": 0, "max": 72 },
        ],
    },
    {
        "_id": ObjectId("000000000000000000000003"),
        "name": "Home & Living",
        "slug": "home-living",
        "accent_color": "#22C55E",
        "hero_image": "https://picsum.photos/seed/cat-home/800/400",
        "attribute_schema": [
            { "key": "finish", "label": "Finish", "type": "text" },
            { "key": "dimensions", "label": "Dimensions", "type": "text" },
        ],
    },
    {
        "_id": ObjectId("000000000000000000000004"),
        "name": "Fitness & Wellness",
        "slug": "fitness-wellness",
        "accent_color": "#F59E0B",
        "hero_image": "https://picsum.photos/seed/cat-fitness/800/400",
        "attribute_schema": [
            { "key": "color", "label": "Color", "type": "select", "options": ["Ocean Teal", "Charcoal", "Coral"] },
            { "key": "size", "label": "Size", "type": "text" },
        ],
    },
]


def _lookup_product(slug_or_id: str, db: Any) -> dict[str, Any] | None:
    """Helper to find product by slug or _id (if valid ObjectId)."""
    col = db[COLLECTION]
    doc = col.find_one({"slug": slug_or_id})
    if doc is None and ObjectId.is_valid(slug_or_id):
        doc = col.find_one({"_id": ObjectId(slug_or_id)})
    return doc


def _format_errors(errors: list[str]) -> dict[str, str]:
    """Convert flat error strings into a field-keyed dictionary for React Hook Form."""
    err_dict = {}
    for err in errors:
        cleaned = err.replace("'", "")
        if "category_id" in err:
            err_dict["category_id"] = cleaned
        elif "title" in err:
            err_dict["title"] = cleaned
        elif "type" in err:
            err_dict["type"] = cleaned
        elif "base_price" in err:
            err_dict["base_price"] = cleaned
        elif "stock_status" in err:
            err_dict["stock_status"] = cleaned
        elif "default_attributes" in err:
            err_dict["default_attributes"] = cleaned
        else:
            err_dict["non_field"] = cleaned
    return err_dict


# ── Categories ─────────────────────────────────────────────────────────────────

@admin_bp.get("/categories")
def api_list_categories():
    db = get_db()
    # Auto-seed categories if empty
    if db["categories"].count_documents({}) == 0:
        db["categories"].insert_many(INITIAL_CATEGORIES)

    categories = list(db["categories"].find({}))
    for cat in categories:
        cat["_id"] = str(cat["_id"])

    return jsonify({"success": True, "data": {"categories": categories}}), 200


# ── Products Listing & Search ──────────────────────────────────────────────────

@admin_bp.get("/products")
def api_list_products():
    db = get_db()
    col = db[COLLECTION]

    # Parse query parameters
    page = max(1, int(request.args.get("page", 1)))
    limit = max(1, int(request.args.get("limit", 10)))
    search = request.args.get("search", "").strip()
    category_id = request.args.get("category_id", "").strip()
    stock_status = request.args.get("stock_status", "").strip()
    is_active_raw = request.args.get("is_active", "").strip()

    # Build Mongo filter query
    query: dict[str, Any] = {}

    if category_id:
        try:
            query["category_id"] = ObjectId(category_id)
        except Exception:
            query["category_id"] = category_id

    if stock_status:
        query["stock_status"] = stock_status

    if is_active_raw:
        query["is_active"] = is_active_raw.lower() in ("true", "1", "yes")

    if search:
        # Match search term against title or tags case-insensitively
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [search]}},
        ]

    total = col.count_documents(query)
    skip = (page - 1) * limit
    cursor = col.find(query).sort([("created_at", -1)]).skip(skip).limit(limit)

    products = [to_list_view(doc) for doc in cursor]
    # In list view, add category_id to help UI matching
    for idx, doc in enumerate(col.find(query).sort([("created_at", -1)]).skip(skip).limit(limit)):
        if "category_id" in doc:
            products[idx]["category_id"] = str(doc["category_id"])

    total_pages = (total + limit - 1) // limit if total > 0 else 0

    pagination = {
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "hasNextPage": page < total_pages,
        "hasPrevPage": page > 1,
    }

    return jsonify({"success": True, "data": {"products": products, "pagination": pagination}}), 200


# ── Product Details ────────────────────────────────────────────────────────────

@admin_bp.get("/products/<slug_or_id>")
def api_get_product(slug_or_id: str):
    db = get_db()
    product = _lookup_product(slug_or_id, db)
    if product is None:
        return jsonify({"success": False, "error": "Product not found."}), 404

    category = db["categories"].find_one({"_id": product.get("category_id")})
    return jsonify({"success": True, "data": to_detail_view(product, category=category)}), 200


# ── Create Product ─────────────────────────────────────────────────────────────

@admin_bp.post("/products")
def api_create_product():
    db = get_db()
    data = request.get_json(silent=True) or {}
    errors = validate_product_payload(data)
    if errors:
        return jsonify({"success": False, "errors": _format_errors(errors)}), 400

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

    # Resolve category slug if missing
    if not doc["category_slug"]:
        cat = db["categories"].find_one({"_id": doc["category_id"]})
        if cat:
            doc["category_slug"] = cat.get("slug", "")

    base_slug = data.get("slug") or generate_slug(data["title"])
    doc["slug"] = ensure_unique_slug(base_slug, db[COLLECTION])

    result = db[COLLECTION].insert_one(doc)
    doc["_id"] = result.inserted_id

    category = db["categories"].find_one({"_id": doc["category_id"]})
    return jsonify({"success": True, "data": to_detail_view(doc, category=category)}), 201


# ── Update Product ─────────────────────────────────────────────────────────────

@admin_bp.put("/products/<slug_or_id>")
def api_update_product(slug_or_id: str):
    db = get_db()
    product = _lookup_product(slug_or_id, db)
    if product is None:
        return jsonify({"success": False, "error": "Product not found."}), 404

    data = request.get_json(silent=True) or {}
    errors = validate_product_payload(data, is_update=True)
    if errors:
        return jsonify({"success": False, "errors": _format_errors(errors)}), 400

    # Category immutability server-side check
    if "category_id" in data and product.get("category_id") and ObjectId(data["category_id"]) != product["category_id"]:
        return jsonify({
            "success": False,
            "errors": {"category_id": "Category cannot be modified after creation."}
        }), 400

    # Fields to update
    set_payload: dict[str, Any] = {"updated_at": utcnow()}

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

    # Update slug if title changes and no explicit slug
    if "slug" in data:
        set_payload["slug"] = ensure_unique_slug(data["slug"], db[COLLECTION], exclude_id=product["_id"])
    elif "title" in data and data["title"] != product.get("title"):
        set_payload["slug"] = ensure_unique_slug(generate_slug(data["title"]), db[COLLECTION], exclude_id=product["_id"])

    db[COLLECTION].update_one({"_id": product["_id"]}, {"$set": set_payload})
    updated = db[COLLECTION].find_one({"_id": product["_id"]})
    category = db["categories"].find_one({"_id": updated.get("category_id")})

    return jsonify({"success": True, "data": to_detail_view(updated, category=category)}), 200


# ── Delete Product ─────────────────────────────────────────────────────────────

@admin_bp.delete("/products/<slug_or_id>")
def api_delete_product(slug_or_id: str):
    db = get_db()
    product = _lookup_product(slug_or_id, db)
    if product is None:
        return jsonify({"success": False, "error": "Product not found."}), 404

    # Soft delete
    db[COLLECTION].update_one(
        {"_id": product["_id"]},
        {"$set": {"is_active": False, "updated_at": utcnow()}}
    )
    return jsonify({"success": True, "message": "Product deactivated."}), 200


# ── Image Management ───────────────────────────────────────────────────────────

@admin_bp.post("/products/<slug_or_id>/images")
def api_upload_image(slug_or_id: str):
    db = get_db()
    product = _lookup_product(slug_or_id, db)
    if product is None:
        return jsonify({"success": False, "error": "Product not found."}), 404

    # React client uses key 'images' for multiple uploads
    files = request.files.getlist("images")
    if not files:
        # Fallback to single 'file' key
        file_obj = request.files.get("file")
        if file_obj:
            files = [file_obj]

    if not files:
        return jsonify({"success": False, "error": "No files provided."}), 400

    uploaded_images = []
    current_images = product.get("images", [])
    has_thumb = any(img.get("isThumbnail") for img in current_images) or bool(product.get("thumbnail"))

    for file in files:
        try:
            # Upload to Cloudinary
            url, public_id = upload_image(file, folder=f"products/{product['slug']}")
            img_id = f"img_{int(time.time() * 1000)}_{len(uploaded_images)}"
            
            # The first image becomes the thumbnail if the product does not have one
            is_thumb = not has_thumb and len(uploaded_images) == 0
            
            new_img = {
                "_id": img_id,
                "url": url,
                "public_id": public_id,
                "isThumbnail": is_thumb
            }
            uploaded_images.append(new_img)
        except Exception as exc:
            return jsonify({"success": False, "error": str(exc)}), 500

    # Save to MongoDB
    all_images = current_images + uploaded_images
    update_data: dict[str, Any] = {"images": all_images}
    
    # Update the thumbnail URL if we set a new thumbnail
    new_thumbnail = next((img["url"] for img in uploaded_images if img["isThumbnail"]), None)
    if new_thumbnail:
        update_data["thumbnail"] = new_thumbnail

    db[COLLECTION].update_one({"_id": product["_id"]}, {"$set": update_data})
    
    return jsonify({"success": True, "data": {"images": all_images}}), 200


@admin_bp.delete("/products/<slug_or_id>/images/<image_id>")
def api_delete_image(slug_or_id: str, image_id: str):
    db = get_db()
    product = _lookup_product(slug_or_id, db)
    if product is None:
        return jsonify({"success": False, "error": "Product not found."}), 404

    current_images = product.get("images", [])
    image_to_delete = next((img for img in current_images if img.get("_id") == image_id), None)
    if not image_to_delete:
        return jsonify({"success": False, "error": "Image not found."}), 404

    # Delete from Cloudinary
    delete_image(image_to_delete["public_id"])

    # Update MongoDB list
    remaining_images = [img for img in current_images if img.get("_id") != image_id]
    update_data: dict[str, Any] = {"images": remaining_images}

    # If the deleted image was the thumbnail, clear the main thumbnail
    if image_to_delete.get("isThumbnail"):
        update_data["thumbnail"] = ""

    db[COLLECTION].update_one({"_id": product["_id"]}, {"$set": update_data})

    return jsonify({"success": True, "message": "Image deleted."}), 200


@admin_bp.put("/products/<slug_or_id>/thumbnail")
def api_set_thumbnail(slug_or_id: str):
    db = get_db()
    product = _lookup_product(slug_or_id, db)
    if product is None:
        return jsonify({"success": False, "error": "Product not found."}), 404

    body = request.get_json(silent=True) or {}
    image_id = body.get("imageId")
    if not image_id:
        return jsonify({"success": False, "error": "'imageId' is required."}), 400

    current_images = product.get("images", [])
    target_image = next((img for img in current_images if img.get("_id") == image_id), None)
    if not target_image:
        return jsonify({"success": False, "error": "Image not found."}), 404

    # Update isThumbnail flag on all images and root thumbnail field
    updated_images = []
    thumbnail_url = ""
    for img in current_images:
        is_target = img.get("_id") == image_id
        img["isThumbnail"] = is_target
        if is_target:
            thumbnail_url = img["url"]
        updated_images.append(img)

    db[COLLECTION].update_one(
        {"_id": product["_id"]},
        {"$set": {"images": updated_images, "thumbnail": thumbnail_url}}
    )

    return jsonify({"success": True, "message": "Thumbnail set successfully."}), 200
