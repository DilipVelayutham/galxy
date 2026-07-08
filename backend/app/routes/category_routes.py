from flask import Blueprint, request, jsonify, g
from bson import ObjectId
from app.db import db
from app.middleware.auth import require_admin
import datetime

category_bp = Blueprint("categories", __name__)

@category_bp.route("/categories", methods=["GET"])
def get_categories():
    query = {"is_active": True}
    categories = list(db.categories.find(query).sort("display_order", 1))
    
    # Format BSON objects
    for cat in categories:
        cat["_id"] = str(cat["_id"])
        
    return jsonify({
        "success": True,
        "data": categories
    }), 200

@category_bp.route("/categories/<slug>", methods=["GET"])
def get_category_by_slug(slug):
    category = db.categories.find_one({"slug": slug, "is_active": True})
    if not category:
        return jsonify({"success": False, "message": "Category not found"}), 404
        
    category["_id"] = str(category["_id"])
    return jsonify({
        "success": True,
        "data": category
    }), 200

@category_bp.route("/admin/categories", methods=["POST"])
@require_admin
def create_category():
    data = request.get_json() or {}
    name = data.get("name")
    slug = data.get("slug")
    description = data.get("description", "")
    cover_image = data.get("cover_image", "")
    banner_image = data.get("banner_image", "")
    accent_color = data.get("accent_color", "pink") # pink, blue, violet, yellow
    display_order = data.get("display_order", 0)
    is_active = data.get("is_active", True)
    
    if not name or not slug:
        return jsonify({"success": False, "message": "Name and slug are required"}), 400
        
    # Check if slug exists
    if db.categories.find_one({"slug": slug}):
        return jsonify({"success": False, "message": "Slug already exists"}), 400
        
    new_cat = {
        "name": name,
        "slug": slug,
        "description": description,
        "cover_image": cover_image,
        "banner_image": banner_image,
        "accent_color": accent_color,
        "display_order": display_order,
        "is_active": is_active,
        "attribute_schema": [],
        "ai_prompt_template": data.get("ai_prompt_template", "A custom neon board featuring {text} in {font} with {color} glow."),
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow()
    }
    
    res = db.categories.insert_one(new_cat)
    new_cat["_id"] = str(res.inserted_id)
    
    return jsonify({
        "success": True,
        "message": "Category created successfully",
        "data": new_cat
    }), 201

@category_bp.route("/admin/categories/<id>", methods=["PUT"])
@require_admin
def update_category(id):
    data = request.get_json() or {}
    category = db.categories.find_one({"_id": ObjectId(id)})
    if not category:
        return jsonify({"success": False, "message": "Category not found"}), 404
        
    update_fields = {}
    for field in ["name", "description", "cover_image", "banner_image", "accent_color", "display_order", "is_active"]:
        if field in data:
            update_fields[field] = data[field]
            
    # Check slug uniqueness if changed
    if "slug" in data and data["slug"] != category["slug"]:
        if db.categories.find_one({"slug": data["slug"]}):
            return jsonify({"success": False, "message": "Slug already exists"}), 400
        update_fields["slug"] = data["slug"]
        
    update_fields["updated_at"] = datetime.datetime.utcnow()
    
    db.categories.update_one({"_id": ObjectId(id)}, {"$set": update_fields})
    
    updated_cat = db.categories.find_one({"_id": ObjectId(id)})
    updated_cat["_id"] = str(updated_cat["_id"])
    
    return jsonify({
        "success": True,
        "message": "Category updated successfully",
        "data": updated_cat
    }), 200

@category_bp.route("/admin/categories/<id>", methods=["DELETE"])
@require_admin
def delete_category(id):
    res = db.categories.delete_one({"_id": ObjectId(id)})
    if res.deleted_count == 0:
        return jsonify({"success": False, "message": "Category not found"}), 404
        
    return jsonify({"success": True, "message": "Category deleted successfully"}), 200

@category_bp.route("/admin/categories/reorder", methods=["PUT"])
@require_admin
def reorder_categories():
    data = request.get_json() or {}
    orders = data.get("order", []) # [{"category_id": "...", "display_order": 1}]
    
    for item in orders:
        cat_id = item.get("category_id")
        disp_order = item.get("display_order")
        if cat_id and disp_order is not None:
            db.categories.update_one({"_id": ObjectId(cat_id)}, {"$set": {"display_order": int(disp_order)}})
            
    return jsonify({"success": True, "message": "Categories reordered successfully"}), 200

@category_bp.route("/admin/categories/<id>/attribute-schema", methods=["PUT"])
@require_admin
def update_attribute_schema(id):
    data = request.get_json() or {}
    schema = data.get("attribute_schema")
    
    if schema is None:
        return jsonify({"success": False, "message": "attribute_schema is required"}), 400
        
    # Validate schema items
    for item in schema:
        if not item.get("key") or not item.get("label") or not item.get("type"):
            return jsonify({"success": False, "message": "Each schema item must have key, label, and type"}), 400
            
    db.categories.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"attribute_schema": schema, "updated_at": datetime.datetime.utcnow()}}
    )
    
    return jsonify({"success": True, "message": "Attribute schema updated successfully"}), 200
