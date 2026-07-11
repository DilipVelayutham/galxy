import math
import re
from datetime import datetime
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.extensions import mongo
from app.auth import require_admin
from app.schemas.order_schema import OrderSchema
from app.services.order_status_service import update_status

admin_bp = Blueprint("admin_orders", __name__)

@admin_bp.route("/orders", methods=["GET"])
@require_admin
def get_admin_orders():
    """
    Returns a paginated, filtered list of all orders including internal admin notes.
    Filters: status, date_from, date_to, search.
    """
    status = request.args.get("status")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    search = request.args.get("search")
    
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        if page < 1 or limit < 1:
            raise ValueError()
    except ValueError:
        return jsonify({"success": False, "message": "Invalid page or limit parameters. Must be positive integers."}), 400

    query = {}
    
    # 1. Filter by status
    if status:
        query["status"] = status
        
    # 2. Filter by date range (created_at)
    date_query = {}
    if date_from:
        try:
            date_query["$gte"] = datetime.fromisoformat(date_from)
        except ValueError:
            return jsonify({"success": False, "message": "Invalid date_from format. Use ISO 8601 format."}), 400
            
    if date_to:
        try:
            date_query["$lte"] = datetime.fromisoformat(date_to)
        except ValueError:
            return jsonify({"success": False, "message": "Invalid date_to format. Use ISO 8601 format."}), 400
            
    if date_query:
        query["created_at"] = date_query
        
    # 3. Filter by search (order_number, customer name, customer phone)
    if search:
        search_escaped = re_escape(search)
        query["$or"] = [
            {"order_number": {"$regex": search_escaped, "$options": "i"}},
            {"customer_snapshot.name": {"$regex": search_escaped, "$options": "i"}},
            {"customer_snapshot.phone": {"$regex": search_escaped, "$options": "i"}}
        ]
        
    # Fetch data and compute counts
    total = mongo.db.orders.count_documents(query)
    
    # Calculate skip offset
    skip = (page - 1) * limit
    
    # Run cursor with sort (newest first)
    orders_cursor = mongo.db.orders.find(query).sort([("created_at", -1)]).skip(skip).limit(limit)
    orders_list = list(orders_cursor)
    
    # Serialize data
    data = OrderSchema(many=True).dump(orders_list)
    pages = math.ceil(total / limit) if total > 0 else 1
    
    return jsonify({
        "success": True,
        "data": data,
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": pages
    }), 200

@admin_bp.route("/orders/<id>", methods=["GET"])
@require_admin
def get_admin_order_detail(id):
    """
    Returns complete order details, including status history and internal admin notes.
    """
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({"success": False, "message": "Invalid order ID format"}), 400
        
    order = mongo.db.orders.find_one({"_id": oid})
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404
        
    data = OrderSchema().dump(order)
    return jsonify({"success": True, "data": data}), 200

@admin_bp.route("/orders/<id>/status", methods=["PUT"])
@require_admin
def update_admin_order_status(id):
    """
    Updates the status of an order, appends to history, and fires notification triggers.
    Enforces forward sequence, cancellation limits, and note requirements.
    """
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({"success": False, "message": "Invalid order ID format"}), 400
        
    body = request.get_json() or {}
    status = body.get("status")
    note = body.get("note")
    customer_visible_note = body.get("customer_visible_note")
    
    if not status:
        return jsonify({"success": False, "message": "Missing 'status' parameter in request body"}), 400
        
    admin_user_id = getattr(request, "admin_user_id", "system")
    
    try:
        updated_order = update_status(
            order_id=oid,
            status=status,
            note=note,
            customer_visible_note=customer_visible_note,
            admin_user_id=admin_user_id
        )
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500
        
    data = OrderSchema().dump(updated_order)
    return jsonify({"success": True, "data": data}), 200

@admin_bp.route("/orders/<id>/quote", methods=["PUT"])
@require_admin
def update_admin_order_quote(id):
    """
    Updates the final quoted price manually Negotiated with customer.
    Must be separate from estimated_total.
    """
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({"success": False, "message": "Invalid order ID format"}), 400
        
    body = request.get_json() or {}
    if "final_quoted_price" not in body:
        return jsonify({"success": False, "message": "Missing 'final_quoted_price' in request body"}), 400
        
    final_quoted_price = body.get("final_quoted_price")
    
    # final_quoted_price can be null or a positive integer
    if final_quoted_price is not None:
        try:
            final_quoted_price = int(final_quoted_price)
            if final_quoted_price < 0:
                raise ValueError()
        except ValueError:
            return jsonify({"success": False, "message": "'final_quoted_price' must be a non-negative integer or null"}), 400
            
    now = datetime.utcnow()
    result = mongo.db.orders.update_one(
        {"_id": oid},
        {"$set": {"final_quoted_price": final_quoted_price, "updated_at": now}}
    )
    
    if result.matched_count == 0:
        return jsonify({"success": False, "message": "Order not found"}), 404
        
    updated_order = mongo.db.orders.find_one({"_id": oid})
    data = OrderSchema().dump(updated_order)
    return jsonify({"success": True, "data": data}), 200

@admin_bp.route("/orders/<id>/notes", methods=["PUT"])
@require_admin
def update_admin_order_notes(id):
    """
    Completely replaces internal admin_notes (working scratchpad).
    Never shown on customer-facing routes.
    """
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({"success": False, "message": "Invalid order ID format"}), 400
        
    body = request.get_json() or {}
    if "admin_notes" not in body:
        return jsonify({"success": False, "message": "Missing 'admin_notes' in request body"}), 400
        
    admin_notes = body.get("admin_notes")
    if admin_notes is not None:
        admin_notes = str(admin_notes)
        
    now = datetime.utcnow()
    result = mongo.db.orders.update_one(
        {"_id": oid},
        {"$set": {"admin_notes": admin_notes, "updated_at": now}}
    )
    
    if result.matched_count == 0:
        return jsonify({"success": False, "message": "Order not found"}), 404
        
    updated_order = mongo.db.orders.find_one({"_id": oid})
    data = OrderSchema().dump(updated_order)
    return jsonify({"success": True, "data": data}), 200

def re_escape(text):
    """Escapes regex special characters to prevent regex injection attacks."""
    import re
    return re.escape(text)
