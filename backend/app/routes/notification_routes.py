from flask import Blueprint, jsonify, g
from bson import ObjectId
from app.db import db
from app.middleware.auth import require_auth
import datetime

notification_bp = Blueprint("notifications", __name__)

@notification_bp.route("/notifications", methods=["GET"])
@require_auth
def get_notifications():
    user_id = g.user["id"]
    notifications = list(
        db.notifications.find({"user_id": ObjectId(user_id)})
        .sort("created_at", -1)
        .limit(50)
    )
    
    unread_count = db.notifications.count_documents({
        "user_id": ObjectId(user_id),
        "is_read": False
    })
    
    formatted = []
    for n in notifications:
        formatted.append({
            "_id": str(n["_id"]),
            "order_id": str(n["order_id"]) if n.get("order_id") else None,
            "message": n["message"],
            "is_read": n["is_read"],
            "created_at": n["created_at"].isoformat()
        })
        
    return jsonify({
        "success": True,
        "data": formatted,
        "unread_count": unread_count
    }), 200

@notification_bp.route("/notifications/<id>/read", methods=["PUT"])
@require_auth
def mark_notification_read(id):
    user_id = g.user["id"]
    res = db.notifications.update_one(
        {"_id": ObjectId(id), "user_id": ObjectId(user_id)},
        {"$set": {"is_read": True}}
    )
    
    if res.matched_count == 0:
        return jsonify({"success": False, "message": "Notification not found"}), 404
        
    return jsonify({"success": True, "message": "Notification marked as read"}), 200

@notification_bp.route("/notifications/read-all", methods=["PUT"])
@require_auth
def mark_all_notifications_read():
    user_id = g.user["id"]
    db.notifications.update_many(
        {"user_id": ObjectId(user_id), "is_read": False},
        {"$set": {"is_read": True}}
    )
    return jsonify({"success": True, "message": "All notifications marked as read"}), 200
