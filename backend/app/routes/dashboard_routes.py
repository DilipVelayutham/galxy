from flask import Blueprint, jsonify
from app.db import db
from app.middleware.auth import require_admin
from bson import ObjectId

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard/stats", methods=["GET"])
@require_admin
def get_dashboard_stats():
    # 1. Orders by status count
    orders_by_status = list(db.orders.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))
    status_counts = {item["_id"]: item["count"] for item in orders_by_status}
    
    # 2. Revenue estimate (delivered/confirmed/in_production/ready/out_for_delivery)
    revenue_query = {
        "status": {"$in": ["confirmed", "in_production", "ready", "out_for_delivery", "delivered"]}
    }
    active_orders = list(db.orders.find(revenue_query))
    
    estimated_revenue = 0.0
    for order in active_orders:
        if order.get("final_quoted_price") is not None:
            estimated_revenue += float(order["final_quoted_price"])
        else:
            estimated_revenue += float(order.get("estimated_total", 0.0))
            
    # 3. Top categories by item ordered
    top_categories = list(db.orders.aggregate([
        {"$unwind": "$items"},
        {"$group": {"_id": "$items.category_name", "orders_count": {"$sum": "$items.quantity"}}},
        {"$sort": {"orders_count": -1}},
        {"$limit": 5}
    ]))
    formatted_cats = [{"category": item["_id"], "count": item["orders_count"]} for item in top_categories]
    
    # 4. Pending reviews
    pending_reviews = db.reviews.count_documents({"is_approved": False})
    
    return jsonify({
        "success": True,
        "data": {
            "status_counts": status_counts,
            "estimated_revenue": estimated_revenue,
            "top_categories": formatted_cats,
            "pending_reviews_count": pending_reviews,
            "total_orders_count": db.orders.count_documents({})
        }
    }), 200

@dashboard_bp.route("/analytics/products", methods=["GET"])
@require_admin
def get_product_analytics():
    products = list(db.products.find({}, {"title": 1, "views": 1, "slug": 1}))
    
    analytics = []
    for prod in products:
        prod_id = prod["_id"]
        
        # Count wishlists containing this product
        wishlist_adds = db.wishlists.count_documents({"product_ids": prod_id})
        
        # Count orders containing this product
        orders_count = db.orders.count_documents({"items.product_id": prod_id})
        
        analytics.append({
            "id": str(prod_id),
            "title": prod.get("title", ""),
            "slug": prod.get("slug", ""),
            "views": prod.get("views", 0),
            "wishlist_count": wishlist_adds,
            "orders_count": orders_count,
            "conversion_rate": round((orders_count / prod.get("views", 1)) * 100, 1) if prod.get("views", 0) > 0 else 0.0
        })
        
    # Sort by orders count descending
    analytics.sort(key=lambda x: x["orders_count"], reverse=True)
    
    return jsonify({
        "success": True,
        "data": analytics
    }), 200

@dashboard_bp.route("/analytics/ai-usage", methods=["GET"])
@require_admin
def get_ai_analytics():
    total_generations = db.ai_generations.count_documents({})
    
    # Category distribution of AI previews
    categories_distribution = list(db.ai_generations.aggregate([
        {"$group": {"_id": "$category_id", "count": {"$sum": 1}}}
    ]))
    
    formatted_dist = []
    for item in categories_distribution:
        cat_id = item["_id"]
        cat = db.categories.find_one({"_id": cat_id})
        formatted_dist.append({
            "category": cat["name"] if cat else "Unknown",
            "count": item["count"]
        })
        
    return jsonify({
        "success": True,
        "data": {
            "total_generations": total_generations,
            "category_distribution": formatted_dist
        }
    }), 200
