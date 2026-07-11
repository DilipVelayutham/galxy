from datetime import datetime
from bson import ObjectId
from app.extensions import mongo
from app.services.order_service import get_order_by_id
from app.services.notification_trigger_service import trigger_order_status_changed

STATUS_SEQUENCE = ["received", "reviewed", "quote_sent", "confirmed", "in_production", "ready", "out_for_delivery", "delivered"]

def update_status(order_id, status, note=None, customer_visible_note=None, admin_user_id="system"):
    """
    Appends a new status to status_history, updates the top-level status field,
    enforces state transition rules, and triggers a customer notification.
    """
    # Normalize order_id to ObjectId
    if isinstance(order_id, str):
        try:
            order_id = ObjectId(order_id)
        except Exception:
            raise ValueError("Invalid order ID format")

    # 1. Fetch order document
    order = get_order_by_id(mongo.db, order_id=order_id)
    if not order:
        raise ValueError("Order not found")
        
    old_status = order.get("status", "received")
    
    # 2. Check if new status is a valid status string
    if status not in STATUS_SEQUENCE and status != "cancelled":
        raise ValueError(f"Invalid status: {status}")
        
    # 3. Check if new status is equal to old status
    if status == old_status:
        raise ValueError(f"Order is already in status: {status}")
        
    # 4. Enforce transition restrictions
    # Cannot transition out of delivered
    if old_status == "delivered":
        raise ValueError("Cannot change status of a delivered order")
        
    # Determine if transition requires a note (backward or cancellation)
    note_required = False
    
    if status == "cancelled":
        note_required = True
    elif old_status == "cancelled":
        # Un-cancelling or moving out of cancelled requires a note
        note_required = True
    else:
        # Both statuses are in the main forward sequence
        old_idx = STATUS_SEQUENCE.index(old_status)
        new_idx = STATUS_SEQUENCE.index(status)
        if new_idx <= old_idx:
            # Backward or same-level status transition
            note_required = True
            
    if note_required:
        if not note or not note.strip():
            raise ValueError("A note is required for backward transitions or cancellation")
            
    # Normalize notes
    clean_note = note.strip() if note else None
    
    # 5. Build and execute updates
    now = datetime.utcnow()
    new_history_entry = {
        "status": status,
        "note": clean_note,
        "updated_by": admin_user_id,
        "timestamp": now
    }
    
    update_fields = {
        "status": status,
        "updated_at": now
    }
    
    if customer_visible_note is not None:
        update_fields["customer_visible_note"] = customer_visible_note
        
    result = mongo.db.orders.update_one(
        {"_id": order_id},
        {
            "$set": update_fields,
            "$push": {"status_history": new_history_entry}
        }
    )
    
    if result.matched_count == 0:
        raise ValueError("Order not found during status update execution")
        
    # 6. Fetch updated document
    updated_order = get_order_by_id(mongo.db, order_id=order_id)
    
    # 7. Trigger order_status_changed notification event
    trigger_order_status_changed(
        user_id=updated_order.get("user_id"),
        order_number=updated_order.get("order_number"),
        status=status,
        note=clean_note
    )
    
    return updated_order
