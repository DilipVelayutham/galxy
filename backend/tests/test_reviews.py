import pytest
import jwt
import json
from datetime import datetime
from bson import ObjectId
from flask import g
from app import create_app
from app.config import Config
from app.db import init_db, get_db, get_reviews_col
from app.services.rating_rollup_service import RatingRollupService

# Test configuration
Config.FLASK_ENV = "testing"
Config.MONGO_URI = "mongomock://localhost"
Config.DB_NAME = "test_reviews_db"

class MockOrderService:
    def __init__(self, eligible=True):
        self.eligible = eligible
        
    def has_delivered_order_for_product(self, user_id, product_id):
        if self.eligible is Exception:
            raise Exception("Connection timeout to order database.")
        return self.eligible

@pytest.fixture
def app():
    # Re-initialize application for tests
    app = create_app(Config)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    # Initialize db with mongomock and yield client database
    db_inst = init_db(force=True)
    # Clear collections
    db_inst["reviews"].delete_many({})
    db_inst["products"].delete_many({})
    db_inst["testimonials"].delete_many({})
    db_inst["users"].delete_many({})
    yield db_inst

@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    """Automatically mocks external services for all tests."""
    import app.services.review_service as rs
    # Default mocks to ensure successful path executions
    monkeypatch.setattr(rs, "order_service", MockOrderService(eligible=True))
    monkeypatch.setattr(rs, "upload_image", lambda file: f"https://res.cloudinary.com/mock/image/upload/test.jpg")

# Helpers to generate JWT token
def generate_token(user_id="user_123", role="customer", name="John Doe", email="john@example.com"):
    payload = {
        "user_id": user_id,
        "role": role,
        "name": name,
        "email": email
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)

def get_auth_headers(user_id="user_123", role="customer", name="John Doe"):
    token = generate_token(user_id, role, name)
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# --- TESTS ---

def test_submit_review_authentication_required(client, db):
    # Call without auth header
    response = client.post(f"/api/products/{ObjectId()}/reviews", json={})
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data["success"] is False
    assert "Authorization token is missing" in data["message"]

def test_submit_review_validation(client, db):
    headers = get_auth_headers()
    prod_id = str(ObjectId())
    
    # Missing fields
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "order_id" in data["errors"]
    assert "order_number" in data["errors"]
    assert "rating" in data["errors"]

    # Invalid rating
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json={
        "order_id": "ord_1",
        "order_number": "ON-100",
        "rating": 6,
        "comment": "Nice"
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "rating" in data["errors"]
    assert "between 1 and 5" in data["errors"]["rating"]

def test_submit_review_not_eligible(client, db, monkeypatch):
    import app.services.review_service as rs
    monkeypatch.setattr(rs, "order_service", MockOrderService(eligible=False))

    headers = get_auth_headers(user_id="user_unauth")
    prod_id = str(ObjectId())
    
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json={
        "order_id": "ord_unauth",
        "order_number": "ON-999",
        "rating": 5,
        "comment": "Nice product"
    })
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data["success"] is False
    assert "purchased and delivered" in data["message"]

def test_submit_review_success_and_duplicate(client, db):
    headers = get_auth_headers(user_id="user_buyer", name="Jane Buyer")
    prod_id = str(ObjectId())
    
    review_payload = {
        "order_id": "ord_buyer_1",
        "order_number": "ON-555",
        "rating": 4,
        "comment": "Good quality",
        "images": ["http://example.com/img1.jpg"]
    }
    
    # 1. First submission should succeed
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json=review_payload)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["message"] == "Review submitted, pending approval"
    assert "id" in data["data"]
    review_id = data["data"]["id"]

    # Verify review in database
    review_doc = db["reviews"].find_one({"_id": ObjectId(review_id)})
    assert review_doc is not None
    assert review_doc["is_approved"] is False
    assert review_doc["customer_name"] == "Jane Buyer"
    assert review_doc["rating"] == 4
    assert review_doc["order_number"] == "ON-555"

    # 2. Duplicate submission with same user, product, and order should fail with 409
    response_dup = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json=review_payload)
    assert response_dup.status_code == 409
    data_dup = json.loads(response_dup.data)
    assert data_dup["success"] is False
    assert "already exists" in data_dup["message"]

    # 3. Submission with different order_id should succeed
    review_payload_diff = review_payload.copy()
    review_payload_diff["order_id"] = "ord_buyer_2"
    response_diff = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json=review_payload_diff)
    assert response_diff.status_code == 201

def test_submit_review_integration_missing_order_service(client, db, monkeypatch):
    import app.services.review_service as rs
    monkeypatch.setattr(rs, "order_service", None)

    headers = get_auth_headers()
    prod_id = str(ObjectId())
    
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json={
        "order_id": "ord_missing",
        "order_number": "ON-MISSING",
        "rating": 5,
        "comment": "Nice product"
    })
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data["success"] is False
    assert "integration error" in data["message"].lower()

def test_submit_review_integration_order_service_throws(client, db, monkeypatch):
    import app.services.review_service as rs
    monkeypatch.setattr(rs, "order_service", MockOrderService(eligible=Exception))

    headers = get_auth_headers()
    prod_id = str(ObjectId())
    
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json={
        "order_id": "ord_throws",
        "order_number": "ON-THROWS",
        "rating": 5,
        "comment": "Nice product"
    })
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data["success"] is False
    assert "integration call error" in data["message"].lower()

def test_submit_review_integration_missing_cloudinary(client, db, monkeypatch):
    import app.services.review_service as rs
    monkeypatch.setattr(rs, "upload_image", None)

    headers = get_auth_headers()
    prod_id = str(ObjectId())
    
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json={
        "order_id": "ord_img_err",
        "order_number": "ON-IMG-ERR",
        "rating": 5,
        "comment": "Nice product",
        "images": ["file1.jpg"]
    })
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data["success"] is False
    assert "Cloudinary helper is currently unavailable" in data["message"]

def test_public_reviews_api(client, db):
    prod_id = ObjectId()
    prod_id_str = str(prod_id)
    
    # Insert multiple reviews
    db["reviews"].insert_many([
        # Approved reviews
        {
            "product_id": prod_id,
            "user_id": "user1",
            "order_id": "ord1",
            "order_number": "ON-1",
            "rating": 3,
            "comment": "Average",
            "images": [],
            "customer_name": "Alice",
            "is_approved": True,
            "is_featured": False,
            "created_at": datetime(2026, 1, 1)
        },
        {
            "product_id": prod_id,
            "user_id": "user2",
            "order_id": "ord2",
            "order_number": "ON-2",
            "rating": 5,
            "comment": "Perfect!",
            "images": ["img.jpg"],
            "customer_name": "Bob",
            "is_approved": True,
            "is_featured": True,
            "created_at": datetime(2026, 1, 2)
        },
        # Pending review (should NOT be returned publicly)
        {
            "product_id": prod_id,
            "user_id": "user3",
            "order_id": "ord3",
            "order_number": "ON-3",
            "rating": 4,
            "comment": "Pending view",
            "images": [],
            "customer_name": "Charlie",
            "is_approved": False,
            "is_featured": False,
            "created_at": datetime(2026, 1, 3)
        }
    ])

    # Fetch public reviews
    response = client.get(f"/api/products/{prod_id_str}/reviews")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["page"] == 1
    assert data["limit"] == 20
    assert data["total"] == 2 # Only approved reviews
    
    # Check that privacy fields (user_id, order_id) are hidden
    for r in data["data"]:
        assert "user_id" not in r
        assert "order_id" not in r
        assert "comment" in r
        assert "rating" in r
        assert "customer_name" in r

    # Check newest sorting default (Bob then Alice)
    assert data["data"][0]["customer_name"] == "Bob"
    assert data["data"][1]["customer_name"] == "Alice"

    # Test sorting: lowest_rated (Alice then Bob)
    response_sort = client.get(f"/api/products/{prod_id_str}/reviews?sort=lowest_rated")
    data_sort = json.loads(response_sort.data)
    assert data_sort["data"][0]["customer_name"] == "Alice"
    assert data_sort["data"][1]["customer_name"] == "Bob"

def test_admin_moderation_flow(client, db):
    prod_id = ObjectId()
    prod_id_str = str(prod_id)
    
    # Create product to rollup update
    db["products"].insert_one({
        "_id": prod_id,
        "name": "Cool Shoes",
        "rating_avg": 0.0,
        "rating_count": 0
    })

    # Submit review
    review_id = db["reviews"].insert_one({
        "product_id": prod_id,
        "user_id": "user_mod",
        "order_id": "ord_mod",
        "order_number": "ON-MOD",
        "rating": 5,
        "comment": "Mod review",
        "images": [],
        "customer_name": "Frank",
        "is_approved": False,
        "is_featured": False,
        "created_at": datetime.utcnow()
    }).inserted_id

    headers_admin = get_auth_headers(role="admin")
    headers_customer = get_auth_headers(role="customer")

    # 1. Check GET /api/admin/reviews restricts customer role
    response_cust = client.get("/api/admin/reviews", headers=headers_customer)
    assert response_cust.status_code == 403

    # 2. Check GET /api/admin/reviews is allowed for admin
    response_admin = client.get("/api/admin/reviews", headers=headers_admin)
    assert response_admin.status_code == 200
    admin_data = json.loads(response_admin.data)
    assert admin_data["total"] == 1
    assert admin_data["data"][0]["user_id"] == "user_mod" # Admin has full info

    # 3. Approve review
    response_app = client.put(f"/api/admin/reviews/{review_id}/approve", headers=headers_admin)
    assert response_app.status_code == 200
    
    # Check approved status and rollup update
    review_doc = db["reviews"].find_one({"_id": review_id})
    assert review_doc["is_approved"] is True
    
    product_doc = db["products"].find_one({"_id": prod_id})
    assert product_doc["rating_avg"] == 5.0
    assert product_doc["rating_count"] == 1

    # 4. Reject review (with reason)
    response_rej = client.put(f"/api/admin/reviews/{review_id}/reject", headers=headers_admin, json={
        "reason": "Inappropriate word"
    })
    assert response_rej.status_code == 200
    
    # Check rejected status, rejection reason, and updated rollup
    review_doc_rej = db["reviews"].find_one({"_id": review_id})
    assert review_doc_rej["is_approved"] is False
    assert review_doc_rej["rejection_reason"] == "Inappropriate word"
    
    product_doc_rej = db["products"].find_one({"_id": prod_id})
    assert product_doc_rej["rating_avg"] == 0.0
    assert product_doc_rej["rating_count"] == 0

    # 5. Promote to testimonial
    response_promo = client.post(f"/api/admin/reviews/{review_id}/promote-to-testimonial", headers=headers_admin)
    assert response_promo.status_code == 200
    promo_data = json.loads(response_promo.data)
    assert "testimonial_id" in promo_data["data"]
    
    # Check testimonials collection
    testi_doc = db["testimonials"].find_one({"_id": ObjectId(promo_data["data"]["testimonial_id"])})
    assert testi_doc is not None
    assert testi_doc["review_id"] == review_id
    assert testi_doc["customer_name"] == "Frank"

    # 6. Delete review (hard delete)
    response_del = client.delete(f"/api/admin/reviews/{review_id}", headers=headers_admin)
    assert response_del.status_code == 200
    
    review_deleted = db["reviews"].find_one({"_id": review_id})
    assert review_deleted is None
