from flask import Blueprint, request, jsonify, g
from bson import ObjectId
from app.db import db
from app.middleware.auth import require_auth, require_admin
from app.services.order_service import OrderService
import datetime

order_bp = Blueprint("orders", __name__)

@order_bp.route("/orders/checkout", methods=["POST"])
@require_auth
def checkout():
    data = request.get_json() or {}
    address_id_str = data.get("address_id")
    
    order_number, err = OrderService.checkout(g.user["id"], address_id_str)
    if err:
        return jsonify({"success": False, "message": err}), 400
        
    return jsonify({
        "success": True,
        "message": "Order placed successfully",
        "data": {
            "order_number": order_number
        }
    }), 201

@order_bp.route("/orders", methods=["GET"])
@require_auth
def get_user_orders():
    user_id = g.user["id"]
    orders = list(db.orders.find({"user_id": ObjectId(user_id)}).sort("created_at", -1))
    
    for order in orders:
        order["_id"] = str(order["_id"])
        order["user_id"] = str(order["user_id"])
        for item in order["items"]:
            item["product_id"] = str(item["product_id"])
            
        # Format datetimes
        order["created_at"] = order["created_at"].isoformat()
        order["updated_at"] = order["updated_at"].isoformat()
        for hist in order.get("status_history", []):
            hist["timestamp"] = hist["timestamp"].isoformat()
            hist["updated_by"] = str(hist["updated_by"])
            
    return jsonify({
        "success": True,
        "data": orders
    }), 200

@order_bp.route("/orders/<order_number>", methods=["GET"])
@require_auth
def get_order_by_number(order_number):
    order = db.orders.find_one({"order_number": order_number})
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404
        
    # Security check: User can only see their own orders unless they are admin
    if str(order["user_id"]) != g.user["id"] and g.user["role"] != "super_admin":
        return jsonify({"success": False, "message": "Unauthorized access to order"}), 403
        
    order["_id"] = str(order["_id"])
    order["user_id"] = str(order["user_id"])
    for item in order["items"]:
        item["product_id"] = str(item["product_id"])
        
    # Format dates
    order["created_at"] = order["created_at"].isoformat()
    order["updated_at"] = order["updated_at"].isoformat()
    for hist in order.get("status_history", []):
        hist["timestamp"] = hist["timestamp"].isoformat()
        hist["updated_by"] = str(hist["updated_by"])
        
    return jsonify({
        "success": True,
        "data": order
    }), 200

@order_bp.route("/admin/orders", methods=["GET"])
@require_admin
def get_admin_orders():
    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    
    query = {}
    if status:
        query["status"] = status
        
    total = db.orders.count_documents(query)
    orders = list(
        db.orders.find(query)
        .skip((page - 1) * limit)
        .limit(limit)
        .sort("created_at", -1)
    )
    
    for order in orders:
        order["_id"] = str(order["_id"])
        order["user_id"] = str(order["user_id"])
        for item in order["items"]:
            item["product_id"] = str(item["product_id"])
        order["created_at"] = order["created_at"].isoformat()
        order["updated_at"] = order["updated_at"].isoformat()
        for hist in order.get("status_history", []):
            hist["timestamp"] = hist["timestamp"].isoformat()
            hist["updated_by"] = str(hist["updated_by"])
            
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    
    return jsonify({
        "success": True,
        "data": orders,
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages
    }), 200

@order_bp.route("/admin/orders/<id>/status", methods=["PUT"])
@require_admin
def update_order_status(id):
    data = request.get_json() or {}
    status = data.get("status")
    note = data.get("note", "")
    
    valid_statuses = [
        "received", "reviewed", "quote_sent", "confirmed",
        "in_production", "ready", "out_for_delivery", "delivered", "cancelled"
    ]
    
    if status not in valid_statuses:
        return jsonify({"success": False, "message": "Invalid order status"}), 400
        
    order = db.orders.find_one({"_id": ObjectId(id)})
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404
        
    status_entry = {
        "status": status,
        "note": note or f"Status updated to {status}.",
        "updated_by": ObjectId(g.user["id"]),
        "timestamp": datetime.datetime.utcnow()
    }
    
    db.orders.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "status": status,
                "customer_visible_note": note or f"Your order is now {status}.",
                "updated_at": datetime.datetime.utcnow()
            },
            "$push": {
                "status_history": status_entry
            }
        }
    )
    
    # Create notification for the customer
    notification_doc = {
        "user_id": order["user_id"],
        "order_id": order["_id"],
        "message": f"Your order {order['order_number']} status has been updated to {status}.",
        "is_read": False,
        "created_at": datetime.datetime.utcnow()
    }
    db.notifications.insert_one(notification_doc)
    
    return jsonify({"success": True, "message": "Order status updated successfully"}), 200

@order_bp.route("/admin/orders/<id>/quote", methods=["PUT"])
@require_admin
def update_order_quote(id):
    data = request.get_json() or {}
    quote = data.get("final_quoted_price")
    
    if quote is None:
        return jsonify({"success": False, "message": "final_quoted_price is required"}), 400
        
    res = db.orders.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "final_quoted_price": float(quote),
                "updated_at": datetime.datetime.utcnow()
            }
        }
    )
    
    if res.matched_count == 0:
        return jsonify({"success": False, "message": "Order not found"}), 404
        
    return jsonify({"success": True, "message": "Order final quote applied successfully"}), 200

@order_bp.route("/admin/orders/<id>/notes", methods=["PUT"])
@require_admin
def update_order_notes(id):
    data = request.get_json() or {}
    admin_notes = data.get("admin_notes", "")
    
    res = db.orders.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "admin_notes": admin_notes,
                "updated_at": datetime.datetime.utcnow()
            }
        }
    )
    
    if res.matched_count == 0:
        return jsonify({"success": False, "message": "Order not found"}), 404
        
    return jsonify({"success": True, "message": "Internal admin notes updated"}), 200
