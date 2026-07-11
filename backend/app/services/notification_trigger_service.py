import logging

logger = logging.getLogger(__name__)

# In-memory queue to capture triggered notifications for assertions in unit tests
triggered_notifications = []

def trigger_order_status_changed(user_id, order_number, status, note=None):
    """
    Triggers the order_status_changed notification for Module 11.
    Payload contract requires: user_id, order_number, status, and note.
    """
    event_data = {
        "event": "order_status_changed",
        "user_id": str(user_id) if user_id else None,
        "order_number": order_number,
        "status": status,
        "note": note
    }
    
    # Store in memory for testing verification
    triggered_notifications.append(event_data)
    
    # Log triggering action
    logger.info(f"Triggered order_status_changed notification event: {event_data}")
    
    return event_data
