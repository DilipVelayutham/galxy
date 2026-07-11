# pyrefly: ignore [missing-import]
import pytest
import os
from datetime import datetime, timedelta, timezone
from app import create_app
# pyrefly: ignore [missing-import]
import mongomock

@pytest.fixture
def app():
    # Setup mock db
    mock_db = mongomock.MongoClient().db
    
    now = datetime.now(timezone.utc)
    # Seed data matching the real schema (category_name inside items)
    mock_db.orders.insert_many([
        {
            "created_at": now - timedelta(days=5),
            "status": "confirmed",
            "updated_at": now - timedelta(days=5),
            "items": [{"category_name": "Lighting"}, {"category_name": "Craft"}]
        },
        {
            "created_at": now - timedelta(days=10),
            "status": "received",
            "updated_at": now - timedelta(hours=25),
            "items": [{"category_name": "Lighting"}]
        },
        {
            "created_at": now - timedelta(days=40),
            "status": "delivered",
            "updated_at": now - timedelta(days=40),
            "items": [{"category_name": "Electronics"}] # outside default 30 days
        },
        {
            "created_at": now - timedelta(hours=2),
            "status": "reviewed",
            "updated_at": now - timedelta(hours=2),
            "items": [{"category_name": "Lighting"}, {"category_name": "Home Decor"}]
        },
        {
            "created_at": now - timedelta(hours=3),
            "status": "cancelled",
            "updated_at": now - timedelta(hours=3),
            "items": [{"category_name": "Home Decor"}]
        }
    ])
    
    os.environ["MONGO_URI"] = "mongodb://mock"
    os.environ["MONGO_DB_NAME"] = "mockdb"
    app = create_app()
    app.config.update({"TESTING": True})
    
    # Override db with mongomock
    import app as app_module
    app_module.db = mock_db
    
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_orders_by_status(app):
    import app as app_module
    db = app_module.db
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=30)
    date_to = now
    
    from app.services.dashboard_service import get_orders_by_status
    results = get_orders_by_status(db, date_from, date_to)
    
    # Check that all 9 expected statuses are present
    statuses = list(results.keys())
    expected_statuses = ["received", "reviewed", "quote_sent", "confirmed", "in_production", "ready", "out_for_delivery", "delivered", "cancelled"]
    assert set(statuses) == set(expected_statuses)
    
    assert results["confirmed"] == 1
    assert results["received"] == 1
    assert results["reviewed"] == 1
    assert results["cancelled"] == 1
    assert results["delivered"] == 0 # outside range

def test_top_categories(app):
    import app as app_module
    db = app_module.db
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=30)
    date_to = now
    
    from app.services.dashboard_service import get_top_categories
    results = get_top_categories(db, date_from, date_to)
    
    # Should be sorted by count descending: Lighting (3) -> Home Decor (2) -> Craft (1)
    assert len(results) == 3
    assert results[0] == {"category_name": "Lighting", "order_count": 3}
    assert results[1] == {"category_name": "Home Decor", "order_count": 2}
    assert results[2] == {"category_name": "Craft", "order_count": 1}

def test_date_range_filtering(app):
    import app as app_module
    db = app_module.db
    now = datetime.now(timezone.utc)
    
    # Custom range: 15 days ago to 4 days ago (includes Order 1, Order 2)
    date_from = now - timedelta(days=15)
    date_to = now - timedelta(days=4)
    
    from app.services.dashboard_service import get_orders_by_status, get_top_categories
    
    status_results = get_orders_by_status(db, date_from, date_to)
    assert status_results["confirmed"] == 1 # Order 1
    assert status_results["received"] == 1 # Order 2
    assert status_results["reviewed"] == 0 # Order 4 (too recent)
    
    cat_results = get_top_categories(db, date_from, date_to)
    assert len(cat_results) == 2
    # Lighting (2 from Order 1, Order 2) -> Craft (1 from Order 1)
    assert cat_results[0] == {"category_name": "Lighting", "order_count": 2}
    assert cat_results[1] == {"category_name": "Craft", "order_count": 1}

def test_api_endpoint_response_shape(client):
    response = client.get('/api/admin/dashboard/stats')
    assert response.status_code == 200
    data = response.json
    assert data["success"] is True
    assert "data" in data
    
    stats = data["data"]
    
    # 6 required top-level fields
    assert "orders_by_status" in stats
    assert "top_categories" in stats
    assert "total_orders_in_range" in stats
    assert "estimated_revenue_in_range" in stats
    assert "pending_review_count" in stats
    assert "pending_reviews_to_moderate" in stats
    
    assert len(stats["orders_by_status"]) == 9

