from flask import Blueprint, request, jsonify, g
from bson import ObjectId
from app.db import db
from app.middleware.auth import require_admin
import datetime

product_bp = Blueprint("products", __name__)

@product_bp.route("/products", methods=["GET"])
def get_products():
    category_slug = request.args.get("category")
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)
    tag = request.args.get("tag")
    featured = request.args.get("featured")
    
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    
    query = {"is_active": True}
    
    if category_slug:
        cat = db.categories.find_one({"slug": category_slug})
        if cat:
            query["category_id"] = cat["_id"]
        else:
            query["category_id"] = None # Will yield empty list
            
    if price_min is not None or price_max is not None:
        query["base_price"] = {}
        if price_min is not None:
            query["base_price"]["$gte"] = price_min
        if price_max is not None:
            query["base_price"]["$lte"] = price_max
            
    if tag:
        query["tags"] = tag
        
    if featured is not None:
        query["is_featured"] = featured.lower() == "true"
        
    total = db.products.count_documents(query)
    
    products = list(
        db.products.find(query)
        .skip((page - 1) * limit)
        .limit(limit)
        .sort("created_at", -1)
    )
    
    # Format and fetch category names
    for prod in products:
        prod["_id"] = str(prod["_id"])
        prod["category_id"] = str(prod["category_id"])
        cat = db.categories.find_one({"_id": ObjectId(prod["category_id"])})
        if cat:
            prod["category_name"] = cat["name"]
            prod["category_slug"] = cat["slug"]
            
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    
    return jsonify({
        "success": True,
        "data": products,
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages
    }), 200

@product_bp.route("/products/<slug>", methods=["GET"])
def get_product_by_slug(slug):
    product = db.products.find_one({"slug": slug, "is_active": True})
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404
        
    # Increment view count
    db.products.update_one({"_id": product["_id"]}, {"$inc": {"views": 1}})
    
    # Format ID
    product["_id"] = str(product["_id"])
    product["category_id"] = str(product["category_id"])
    
    # Pre-hydrate category schema
    cat = db.categories.find_one({"_id": ObjectId(product["category_id"])})
    if cat:
        cat["_id"] = str(cat["_id"])
        product["category"] = cat
        
    return jsonify({
        "success": True,
        "data": product
    }), 200

@product_bp.route("/products/search", methods=["GET"])
def search_products():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"success": True, "data": []}), 200
        
    query = {
        "is_active": True,
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}}
        ]
    }
    
    products = list(db.products.find(query).limit(20))
    for prod in products:
        prod["_id"] = str(prod["_id"])
        prod["category_id"] = str(prod["category_id"])
        
    return jsonify({
        "success": True,
        "data": products
    }), 200

@product_bp.route("/admin/products", methods=["POST"])
@require_admin
def create_product():
    data = request.get_json() or {}
    category_id = data.get("category_id")
    title = data.get("title")
    slug = data.get("slug")
    prod_type = data.get("type", "pre_designed") # pre_designed, fully_custom
    base_price = data.get("base_price", 0)
    images = data.get("images", [])
    thumbnail = data.get("thumbnail", "")
    description = data.get("description", "")
    specifications = data.get("specifications", {})
    default_attributes = data.get("default_attributes", {})
    stock_status = data.get("stock_status", "in_stock") # in_stock, made_to_order, out_of_stock
    tags = data.get("tags", [])
    is_featured = data.get("is_featured", False)
    is_active = data.get("is_active", True)
    
    if not category_id or not title or not slug:
        return jsonify({"success": False, "message": "category_id, title, and slug are required"}), 400
        
    # Check slug uniqueness
    if db.products.find_one({"slug": slug}):
        return jsonify({"success": False, "message": "Product slug already exists"}), 400
        
    new_prod = {
        "category_id": ObjectId(category_id),
        "title": title,
        "slug": slug,
        "type": prod_type,
        "base_price": float(base_price),
        "images": images,
        "thumbnail": thumbnail or (images[0] if images else ""),
        "description": description,
        "specifications": specifications,
        "default_attributes": default_attributes,
        "stock_status": stock_status,
        "tags": tags,
        "is_featured": is_featured,
        "is_active": is_active,
        "views": 0,
        "rating_avg": 0,
        "rating_count": 0,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow()
    }
    
    res = db.products.insert_one(new_prod)
    new_prod["_id"] = str(res.inserted_id)
    new_prod["category_id"] = str(new_prod["category_id"])
    
    return jsonify({
        "success": True,
        "message": "Product created successfully",
        "data": new_prod
    }), 201

@product_bp.route("/admin/products/<id>", methods=["PUT"])
@require_admin
def update_product(id):
    data = request.get_json() or {}
    product = db.products.find_one({"_id": ObjectId(id)})
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404
        
    update_fields = {}
    
    # Standard field copy
    for field in ["title", "type", "description", "specifications", "default_attributes", "stock_status", "tags", "is_featured", "is_active", "images", "thumbnail"]:
        if field in data:
            update_fields[field] = data[field]
            
    if "base_price" in data:
        update_fields["base_price"] = float(data["base_price"])
        
    if "category_id" in data:
        update_fields["category_id"] = ObjectId(data["category_id"])
        
    if "slug" in data and data["slug"] != product["slug"]:
        if db.products.find_one({"slug": data["slug"]}):
            return jsonify({"success": False, "message": "Product slug already exists"}), 400
        update_fields["slug"] = data["slug"]
        
    update_fields["updated_at"] = datetime.datetime.utcnow()
    
    db.products.update_one({"_id": ObjectId(id)}, {"$set": update_fields})
    
    updated_prod = db.products.find_one({"_id": ObjectId(id)})
    updated_prod["_id"] = str(updated_prod["_id"])
    updated_prod["category_id"] = str(updated_prod["category_id"])
    
    return jsonify({
        "success": True,
        "message": "Product updated successfully",
        "data": updated_prod
    }), 200

@product_bp.route("/admin/products/<id>", methods=["DELETE"])
@require_admin
def delete_product(id):
    res = db.products.delete_one({"_id": ObjectId(id)})
    if res.deleted_count == 0:
        return jsonify({"success": False, "message": "Product not found"}), 404
        
    return jsonify({"success": True, "message": "Product deleted successfully"}), 200

@product_bp.route("/admin/products/<id>/images", methods=["POST"])
@require_admin
def upload_product_image(id):
    # Cloudinary upload endpoints will be handled through standard client-side direct-to-cloudinary uploads,
    # but we can implement a sign-signature or mock upload for completeness.
    # We will provide a standard file uploader endpoint using the Cloudinary library if configured, or mock.
    file = request.files.get("image")
    if not file:
        return jsonify({"success": False, "message": "No image file provided"}), 400
        
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Setup config
        cloudinary.config(
            cloud_name=g.app.config.get("CLOUDINARY_CLOUD_NAME"),
            api_key=g.app.config.get("CLOUDINARY_API_KEY"),
            api_secret=g.app.config.get("CLOUDINARY_API_SECRET")
        )
        
        upload_result = cloudinary.uploader.upload(file)
        url = upload_result.get("secure_url")
        
        # Append image url to product
        db.products.update_one({"_id": ObjectId(id)}, {"$push": {"images": url}})
        
        return jsonify({
            "success": True,
            "message": "Image uploaded successfully",
            "url": url
        }), 200
        
    except Exception as e:
        # Fallback to local file mock url in development
        mock_url = f"https://res.cloudinary.com/demo/image/upload/sample.jpg"
        db.products.update_one({"_id": ObjectId(id)}, {"$push": {"images": mock_url}})
        return jsonify({
            "success": True,
            "message": f"Image mock upload (Dev Mode): {str(e)}",
            "url": mock_url
        }), 200
