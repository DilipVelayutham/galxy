from flask import Blueprint, jsonify, g
from bson import ObjectId
from app.db import db
from app.middleware.auth import require_auth
import datetime

wishlist_bp = Blueprint("wishlist", __name__)

@wishlist_bp.route("", methods=["GET"])
@require_auth
def get_wishlist():
    user_id = g.user["id"]
    wishlist = db.wishlists.find_one({"user_id": ObjectId(user_id)})
    
    if not wishlist:
        wishlist = {"user_id": ObjectId(user_id), "product_ids": [], "updated_at": datetime.datetime.utcnow()}
        db.wishlists.insert_one(wishlist)
        
    product_ids = wishlist.get("product_ids", [])
    
    # Hydrate products
    products = list(db.products.find({"_id": {"$in": product_ids}, "is_active": True}))
    for prod in products:
        prod["_id"] = str(prod["_id"])
        prod["category_id"] = str(prod["category_id"])
        
    return jsonify({
        "success": True,
        "data": products
    }), 200

@wishlist_bp.route("/<product_id>", methods=["POST"])
@require_auth
def add_to_wishlist(product_id):
    user_id = g.user["id"]
    
    # Check if product exists and is active
    product = db.products.find_one({"_id": ObjectId(product_id), "is_active": True})
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404
        
    wishlist = db.wishlists.find_one({"user_id": ObjectId(user_id)})
    if not wishlist:
        wishlist = {"user_id": ObjectId(user_id), "product_ids": [], "updated_at": datetime.datetime.utcnow()}
        db.wishlists.insert_one(wishlist)
        
    product_ids = wishlist.get("product_ids", [])
    
    if ObjectId(product_id) not in product_ids:
        product_ids.append(ObjectId(product_id))
        db.wishlists.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": {"product_ids": product_ids, "updated_at": datetime.datetime.utcnow()}}
        )
        
    return jsonify({"success": True, "message": "Product added to wishlist successfully"}), 200

@wishlist_bp.route("/<product_id>", methods=["DELETE"])
@require_auth
def remove_from_wishlist(product_id):
    user_id = g.user["id"]
    wishlist = db.wishlists.find_one({"user_id": ObjectId(user_id)})
    if not wishlist:
        return jsonify({"success": False, "message": "Wishlist not found"}), 404
        
    product_ids = wishlist.get("product_ids", [])
    
    if ObjectId(product_id) in product_ids:
        product_ids.remove(ObjectId(product_id))
        db.wishlists.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": {"product_ids": product_ids, "updated_at": datetime.datetime.utcnow()}}
        )
        
    return jsonify({"success": True, "message": "Product removed from wishlist successfully"}), 200
