import pytest
import jwt
import json
from datetime import datetime
from bson import ObjectId
from flask import g
from app import create_app
from app.configs.env_config import Config
from app.db import init_db, get_db, get_reviews_col
from app.services.rating_rollup_service import RatingRollupService

# Test configuration
Config.FLASK_ENV = "testing"
Config.MONGO_URI = "mongomock://localhost"
Config.DB_NAME = "test_reviews_db"

class MockOrderService:
    def __init__(self, eligible=True, order_id="ord_buyer_123", order_number="ON-555"):
        self.eligible = eligible
        self.order_id = order_id
        self.order_number = order_number
        
    def has_delivered_order_for_product(self, user_id, product_id):
        if self.eligible is Exception:
            raise Exception("Connection timeout to order database.")
        if not self.eligible:
            return False
        # Return structured order information
        return {
            "order_id": self.order_id,
            "order_number": self.order_number
        }

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

def test_database_indexes(db):
    # Check reviews collection indexes
    reviews_indexes = db["reviews"].index_information()
    assert "product_id_1" in reviews_indexes
    assert "is_approved_1" in reviews_indexes
    assert "user_id_1_order_id_1" in reviews_indexes  # Compound index
    assert "created_at_1" in reviews_indexes

    # Check testimonials collection indexes
    testimonials_indexes = db["testimonials"].index_information()
    assert "is_active_1" in testimonials_indexes
    assert "display_order_1" in testimonials_indexes

def test_submit_review_authentication_required(client, db):
    # Call without auth header
    response = client.post(f"/api/products/{ObjectId()}/reviews", json={})
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data["success"] is False
    assert "errors" in data

def test_submit_review_validation(client, db):
    headers = get_auth_headers()
    prod_id = str(ObjectId())
    
    # Missing rating
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "rating" in data["errors"]

    # Invalid rating
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json={
        "rating": 6,
        "comment": "Nice"
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "rating" in data["errors"]
    assert "between 1 and 5" in data["errors"]["rating"]

    # Invalid comment length
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json={
        "rating": 4,
        "comment": "A" * 2001
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "comment" in data["errors"]

    # Invalid images payload type
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json={
        "rating": 4,
        "images": "invalid_string_format"
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "images" in data["errors"]

def test_submit_review_not_eligible(client, db, monkeypatch):
    import app.services.review_service as rs
    monkeypatch.setattr(rs, "order_service", MockOrderService(eligible=False))

    headers = get_auth_headers(user_id="user_unauth")
    prod_id = str(ObjectId())
    
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json={
        "rating": 5,
        "comment": "Nice product"
    })
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data["success"] is False
    assert data["message"] == "not a verified delivered purchase"

def test_submit_review_success_and_duplicate(client, db):
    headers = get_auth_headers(user_id="user_buyer", name="Jane Buyer")
    prod_id = str(ObjectId())
    
    review_payload = {
        "rating": 4,
        "comment": "Good quality",
        "images": ["http://example.com/img1.jpg"]
    }
    
    # 1. First submission should succeed (order metadata determined server-side)
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json=review_payload)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["message"] == "Review submitted, pending approval"
    assert "id" in data["data"]
    review_id = data["data"]["id"]

    # Verify review in database contains server-side resolved order values
    review_doc = db["reviews"].find_one({"_id": ObjectId(review_id)})
    assert review_doc is not None
    assert review_doc["is_approved"] is False
    assert review_doc["customer_name"] == "Jane Buyer"
    assert review_doc["rating"] == 4
    assert review_doc["order_id"] == "ord_buyer_123"
    assert review_doc["order_number"] == "ON-555"

    # 2. Duplicate submission for same user/product/order should fail with 409 and exact message
    response_dup = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json=review_payload)
    assert response_dup.status_code == 409
    data_dup = json.loads(response_dup.data)
    assert data_dup["success"] is False
    assert data_dup["message"] == "You've already reviewed this order's purchase of this product"

def test_public_reviews_api_fields(client, db):
    prod_id = ObjectId()
    prod_id_str = str(prod_id)
    
    db["reviews"].insert_one({
        "product_id": prod_id,
        "user_id": "user1",
        "order_id": "ord1",
        "order_number": "ON-1",
        "rating": 5,
        "comment": "Average description",
        "images": ["img.jpg"],
        "customer_name": "Alice",
        "is_approved": True,
        "is_featured": False,
        "created_at": datetime(2026, 1, 1),
        "updated_at": datetime(2026, 1, 1)
    })

    # Fetch public reviews
    response = client.get(f"/api/products/{prod_id_str}/reviews")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert len(data["data"]) == 1
    
    # Verify ONLY public fields are exposed
    public_review = data["data"][0]
    allowed_keys = {"id", "_id", "customer_name", "rating", "comment", "images", "created_at"}
    for key in public_review.keys():
        assert key in allowed_keys
    
    assert "user_id" not in public_review
    assert "order_id" not in set(public_review.keys())
    assert "is_approved" not in public_review

def test_admin_moderation_flow_and_testimonial_promotion(client, db, monkeypatch):
    prod_id = ObjectId()
    prod_id_str = str(prod_id)
    
    db["products"].insert_one({
        "_id": prod_id,
        "name": "Cool Shoes",
        "rating_avg": 0.0,
        "rating_count": 0
    })

    review_id = db["reviews"].insert_one({
        "product_id": prod_id,
        "user_id": "user_mod",
        "order_id": "ord_mod",
        "order_number": "ON-MOD",
        "rating": 5,
        "comment": "Mod review comments",
        "images": ["img1.jpg"],
        "customer_name": "Frank",
        "is_approved": False,
        "is_featured": False,
        "created_at": datetime.utcnow()
    }).inserted_id

    headers_admin = get_auth_headers(role="admin")

    # 1. Attempting to promote unapproved review must fail
    response_promo_fail = client.post(f"/api/admin/reviews/{review_id}/promote-to-testimonial", headers=headers_admin, json={
        "customer_location": "New York, USA",
        "display_order": 1
    })
    assert response_promo_fail.status_code == 400
    data_promo_fail = json.loads(response_promo_fail.data)
    assert "Only approved reviews" in data_promo_fail["message"]

    # 2. Approve review (must return the updated review object in data)
    response_app = client.put(f"/api/admin/reviews/{review_id}/approve", headers=headers_admin)
    assert response_app.status_code == 200
    data_app = json.loads(response_app.data)
    assert data_app["success"] is True
    assert "review" in data_app["data"]
    assert data_app["data"]["review"]["is_approved"] is True

    # 3. Promote approved review with invalid customer_location length
    response_promo_loc_fail = client.post(f"/api/admin/reviews/{review_id}/promote-to-testimonial", headers=headers_admin, json={
        "customer_location": "A" * 101,
        "display_order": 1
    })
    assert response_promo_loc_fail.status_code == 400

    # 4. Promote approved review successfully
    response_promo = client.post(f"/api/admin/reviews/{review_id}/promote-to-testimonial", headers=headers_admin, json={
        "customer_location": "New York, USA",
        "display_order": 5
    })
    assert response_promo.status_code == 200
    promo_data = json.loads(response_promo.data)
    
    # Check testimonials collection structure strictly
    testi_doc = db["testimonials"].find_one({"_id": ObjectId(promo_data["data"]["testimonial_id"])})
    assert testi_doc is not None
    assert testi_doc["source"] == "review"
    assert testi_doc["review_id"] == review_id
    assert testi_doc["customer_name"] == "Frank"
    assert testi_doc["customer_location"] == "New York, USA"
    assert testi_doc["quote"] == "Mod review comments"
    assert testi_doc["rating"] == 5
    assert testi_doc["image"] == "img1.jpg"
    assert testi_doc["display_order"] == 5
    assert testi_doc["is_active"] is True

def test_submit_review_integration_invalid_return_format(client, db, monkeypatch):
    import app.services.review_service as rs
    
    class MockOrderServiceBool:
        def has_delivered_order_for_product(self, user_id, product_id):
            return True
            
    monkeypatch.setattr(rs, "order_service", MockOrderServiceBool())

    headers = get_auth_headers()
    prod_id = str(ObjectId())
    
    response = client.post(f"/api/products/{prod_id}/reviews", headers=headers, json={
        "rating": 5,
        "comment": "Nice product"
    })
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data["success"] is False
    assert "Invalid response format" in data["message"]
