from datetime import datetime, timedelta, timezone
from typing import List, Dict

def get_dashboard_stats_data(db, date_from_str=None, date_to_str=None):
    # Determine date range (default to last 30 days)
    now = datetime.now(timezone.utc)
    
    if date_to_str:
        date_to = datetime.fromisoformat(date_to_str.replace('Z', '+00:00'))
    else:
        date_to = now
        
    if date_from_str:
        date_from = datetime.fromisoformat(date_from_str.replace('Z', '+00:00'))
    else:
        date_from = now - timedelta(days=30)

    # Team Lead's KPIs
    kpi_stats = get_kpi_stats(db, date_from, date_to)

    # Member 2's chart aggregations
    orders_by_status = get_orders_by_status(db, date_from, date_to)
    top_categories = get_top_categories(db, date_from, date_to)

    return {
        "orders_by_status": orders_by_status,
        "total_orders_in_range": kpi_stats["total_orders_in_range"],
        "estimated_revenue_in_range": kpi_stats["estimated_revenue_in_range"],
        "pending_review_count": kpi_stats["pending_review_count"],
        "pending_reviews_to_moderate": kpi_stats["pending_reviews_to_moderate"],
        "top_categories": top_categories
    }


def get_orders_by_status(db, date_from: datetime, date_to: datetime) -> Dict[str, int]:
    """Return dict of order counts per status within the given date range.
    Expected statuses: received, reviewed, quote_sent, confirmed, in_production, ready,
    out_for_delivery, delivered, cancelled.
    """
    match_stage = {"$match": {"created_at": {"$gte": date_from, "$lte": date_to}}}
    group_stage = {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    project_stage = {"$project": {"status": "$_id", "count": 1, "_id": 0}}
    pipeline = [match_stage, group_stage, project_stage]
    results = list(db.orders.aggregate(pipeline))
    expected_statuses = ["received", "reviewed", "quote_sent", "confirmed", "in_production", "ready", "out_for_delivery", "delivered", "cancelled"]
    status_map = {r["status"]: r["count"] for r in results}
    return {s: status_map.get(s, 0) for s in expected_statuses}


def get_top_categories(db, date_from: datetime, date_to: datetime) -> List[Dict]:
    """Return top categories by order count within the date range.
    Each entry contains 'category_name' and 'order_count', sorted descending.
    """
    match_stage = {"$match": {"created_at": {"$gte": date_from, "$lte": date_to}}}
    unwind_items = {"$unwind": "$items"}
    group_stage = {"$group": {"_id": "$items.category_name", "order_count": {"$sum": 1}}}
    sort_stage = {"$sort": {"order_count": -1}}
    project_stage = {"$project": {"category_name": "$_id", "order_count": 1, "_id": 0}}
    pipeline = [match_stage, unwind_items, group_stage, sort_stage, project_stage]
    return list(db.orders.aggregate(pipeline))

def get_kpi_stats(db, date_from: datetime, date_to: datetime) -> Dict:
    # 1. Total Orders & Estimated Revenue
    match_stage = {"$match": {"created_at": {"$gte": date_from, "$lte": date_to}}}
    group_stage = {
        "$group": {
            "_id": None,
            "total_orders": {"$sum": 1},
            "estimated_revenue": {
                "$sum": {
                    "$ifNull": ["$final_quoted_price", {"$ifNull": ["$estimated_total", 0]}]
                }
            }
        }
    }
    revenue_pipeline = [match_stage, group_stage]
    revenue_result = list(db.orders.aggregate(revenue_pipeline))
    if revenue_result:
        total_orders = revenue_result[0].get("total_orders", 0)
        estimated_revenue = revenue_result[0].get("estimated_revenue", 0)
    else:
        total_orders = 0
        estimated_revenue = 0

    # 2. Pending Review Count (Orders in received or reviewed > 24h old)
    twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    pending_orders_count = db.orders.count_documents({
        "status": {"$in": ["received", "reviewed"]},
        "created_at": {"$lte": twenty_four_hours_ago}
    })

    # 3. Pending Reviews to Moderate
    pending_reviews = db.reviews.count_documents({"status": "pending"})

    return {
        "total_orders_in_range": total_orders,
        "estimated_revenue_in_range": estimated_revenue,
        "pending_review_count": pending_orders_count,
        "pending_reviews_to_moderate": pending_reviews
    }
