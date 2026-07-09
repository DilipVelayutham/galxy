import pytest
from bson import ObjectId
from datetime import datetime, timezone
from io import BytesIO
from unittest.mock import patch

@pytest.fixture(autouse=True)
def setup_admin_data(db):
    """
    Clears test collections and inserts mock categories and products.
    """
    db.categories.drop()
    db.products.drop()
    
    # Insert mock categories
    db.categories.insert_many([
        {
            "_id": ObjectId("60c72b2f9b1d8b2e1c8d5678"),
            "name": "Neon Name Boards",
            "slug": "neon-name-boards",
            "is_active": True,
            "attribute_schema": [
                {
                    "key": "font",
                    "label": "Font Style",
                    "type": "select",
                    "options": [
                        { "value": "cursive", "label": "Cursive Style", "price_delta": 0 },
                        { "value": "bold", "label": "Bold Line Style", "price_delta": 150 }
                    ],
                    "required": True
                },
                {
                    "key": "color",
                    "label": "Neon Glow Color",
                    "type": "color_swatch",
                    "options": [
                        { "value": "blue", "label": "Electric Blue", "price_delta": 0 },
                        { "value": "pink", "label": "Hot Pink", "price_delta": 100 }
                    ],
                    "required": True
                }
            ],
            "accent_color": "#18E7FF"
        },
        {
            "_id": ObjectId("60c72b2f9b1d8b2e1c8d5679"),
            "name": "Quilling Art",
            "slug": "quilling-art",
            "is_active": False, # Inactive Category
            "attribute_schema": [],
            "accent_color": "#FF2E8A"
        }
    ])
    
    # Insert mock products
    db.products.insert_many([
        {
            "_id": ObjectId("60c72b2f9b1d8b2e1c8d0001"),
            "category_id": ObjectId("60c72b2f9b1d8b2e1c8d5678"),
            "category_slug": "neon-name-boards",
            "title": "Neon Light 1",
            "slug": "neon-light-1",
            "type": "pre_designed",
            "base_price": 1000.0,
            "images": [
                {"url": "https://res.cloudinary.com/v6m2kkn9/image/upload/image1.jpg", "public_id": "img1"}
            ],
            "thumbnail": "https://res.cloudinary.com/v6m2kkn9/image/upload/image1.jpg",
            "description": "Awesome light",
            "stock_status": "in_stock",
            "tags": ["bestseller"],
            "is_featured": True,
            "is_active": True,
            "views": 10,
            "rating_avg": 4.5,
            "rating_count": 1,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ])

# Helper headers
def get_auth_headers(token="test-admin-token"):
    return {
        "Authorization": f"Bearer {token}"
    }

def test_admin_auth_checks(client):
    """
    Ensures that access without token is blocked with 401, 
    and invalid token is blocked with 403.
    """
    # No headers
    response = client.get("/api/admin/products")
    assert response.status_code == 401
    
    # Wrong token
    response = client.get("/api/admin/products", headers=get_auth_headers("wrong-token"))
    assert response.status_code == 403

def test_get_admin_products(client):
    """
    Admin should be able to fetch all products including inactive ones.
    """
    response = client.get("/api/admin/products", headers=get_auth_headers())
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1

def test_create_product_success(client, db):
    payload = {
        "category_id": "60c72b2f9b1d8b2e1c8d5678",
        "title": "Neon Light 2",
        "type": "fully_custom",
        "base_price": 1500.0,
        "description": "New customizable sign",
        "stock_status": "made_to_order",
        "default_attributes": {
            "font": "bold",
            "color": "pink"
        },
        "tags": ["new", "custom"],
        "is_featured": False,
        "is_active": True
    }
    
    # Image count soft check warning should trigger since images is initially empty
    response = client.post("/api/admin/products", json=payload, headers=get_auth_headers())
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "Admin Warning" in json_data["message"]
    
    data = json_data["data"]
    assert data["title"] == "Neon Light 2"
    assert data["slug"] == "neon-light-2"
    assert data["category_slug"] == "neon-name-boards"
    assert data["views"] == 0
    assert data["rating_avg"] == 0.0

def test_create_product_validation(client):
    headers = get_auth_headers()
    
    # 1. Invalid title length
    payload = {
        "category_id": "60c72b2f9b1d8b2e1c8d5678",
        "title": "Hi",
        "type": "pre_designed",
        "base_price": 1000.0,
        "stock_status": "in_stock"
    }
    res = client.post("/api/admin/products", json=payload, headers=headers)
    assert res.status_code == 400
    assert "title" in res.get_json()["errors"]
    
    # 2. Negative base price
    payload = {
        "category_id": "60c72b2f9b1d8b2e1c8d5678",
        "title": "Neon Valid Title",
        "type": "pre_designed",
        "base_price": -50.0,
        "stock_status": "in_stock"
    }
    res = client.post("/api/admin/products", json=payload, headers=headers)
    assert res.status_code == 400
    assert "base_price" in res.get_json()["errors"]
    
    # 3. Reference to inactive category
    payload = {
        "category_id": "60c72b2f9b1d8b2e1c8d5679", # Inactive category
        "title": "Neon Valid Title",
        "type": "pre_designed",
        "base_price": 1000.0,
        "stock_status": "in_stock"
    }
    res = client.post("/api/admin/products", json=payload, headers=headers)
    assert res.status_code == 400
    assert "category_id" in res.get_json()["errors"]
    
    # 4. Invalid default attributes (attribute key not in schema)
    payload = {
        "category_id": "60c72b2f9b1d8b2e1c8d5678",
        "title": "Neon Valid Title",
        "type": "pre_designed",
        "base_price": 1000.0,
        "stock_status": "in_stock",
        "default_attributes": {
            "invalid_key": "some_value"
        }
    }
    res = client.post("/api/admin/products", json=payload, headers=headers)
    assert res.status_code == 400
    assert "default_attributes" in res.get_json()["errors"]
    
    # 5. Invalid default attributes option value
    payload = {
        "category_id": "60c72b2f9b1d8b2e1c8d5678",
        "title": "Neon Valid Title",
        "type": "pre_designed",
        "base_price": 1000.0,
        "stock_status": "in_stock",
        "default_attributes": {
            "font": "gothic" # Not in font options (cursive, bold)
        }
    }
    res = client.post("/api/admin/products", json=payload, headers=headers)
    assert res.status_code == 400
    assert "default_attributes" in res.get_json()["errors"]

def test_update_product_disallowed_category_change(client):
    headers = get_auth_headers()
    payload = {
        "category_id": "60c72b2f9b1d8b2e1c8d5679"
    }
    # Trying to change category_id is blocked
    res = client.put("/api/admin/products/60c72b2f9b1d8b2e1c8d0001", json=payload, headers=headers)
    assert res.status_code == 400
    assert "category_id" in res.get_json()["errors"]

def test_update_product_title_slug_regeneration(client, db):
    headers = get_auth_headers()
    payload = {
        "title": "Neon Light 1 Updated"
    }
    # Update title
    res = client.put("/api/admin/products/60c72b2f9b1d8b2e1c8d0001", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["title"] == "Neon Light 1 Updated"
    assert data["slug"] == "neon-light-1-updated"

def test_soft_delete_product(client, db):
    headers = get_auth_headers()
    res = client.delete("/api/admin/products/60c72b2f9b1d8b2e1c8d0001", headers=headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["is_active"] is False
    
    # Confirm soft deleted in DB
    doc = db.products.find_one({"_id": ObjectId("60c72b2f9b1d8b2e1c8d0001")})
    assert doc["is_active"] is False

@patch("app.utils.cloudinary_helper.cloudinary.uploader.upload")
def test_upload_images(mock_upload, client, db):
    # Mock Cloudinary SDK response
    mock_upload.return_value = {
        "secure_url": "https://res.cloudinary.com/v6m2kkn9/image/upload/sample_uploaded.jpg",
        "public_id": "galxy/products/sample_uploaded"
    }
    
    headers = get_auth_headers()
    data = {
        "images": (BytesIO(b"dummy image data"), "test.jpg")
    }
    
    res = client.post(
        "/api/admin/products/60c72b2f9b1d8b2e1c8d0001/images",
        data=data,
        content_type="multipart/form-data",
        headers=headers
    )
    assert res.status_code == 200
    json_data = res.get_json()["data"]
    
    # Should append image
    assert len(json_data["images"]) == 2
    assert json_data["images"][1]["url"] == "https://res.cloudinary.com/v6m2kkn9/image/upload/sample_uploaded.jpg"
    assert json_data["images"][1]["public_id"] == "galxy/products/sample_uploaded"

@patch("app.utils.cloudinary_helper.cloudinary.uploader.destroy")
def test_delete_image(mock_destroy, client, db):
    mock_destroy.return_value = {"result": "ok"}
    
    headers = get_auth_headers()
    payload = {
        "image_url": "https://res.cloudinary.com/v6m2kkn9/image/upload/image1.jpg"
    }
    
    # Deleting the thumbnail (image1.jpg) should reset the thumbnail to None
    res = client.delete(
        "/api/admin/products/60c72b2f9b1d8b2e1c8d0001/images",
        json=payload,
        headers=headers
    )
    assert res.status_code == 200
    json_data = res.get_json()["data"]
    
    assert len(json_data["images"]) == 0
    assert json_data["thumbnail"] is None

def test_set_thumbnail_success(client, db):
    # First, let's inject a second image to switch between
    db.products.update_one(
        {"_id": ObjectId("60c72b2f9b1d8b2e1c8d0001")},
        {"$push": {"images": {"url": "https://res.cloudinary.com/v6m2kkn9/image/upload/image2.jpg", "public_id": "img2"}}}
    )
    
    headers = get_auth_headers()
    payload = {
        "image_url": "https://res.cloudinary.com/v6m2kkn9/image/upload/image2.jpg"
    }
    
    res = client.put(
        "/api/admin/products/60c72b2f9b1d8b2e1c8d0001/thumbnail",
        json=payload,
        headers=headers
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["thumbnail"] == "https://res.cloudinary.com/v6m2kkn9/image/upload/image2.jpg"

def test_set_thumbnail_invalid_url(client):
    headers = get_auth_headers()
    payload = {
        "image_url": "https://res.cloudinary.com/v6m2kkn9/image/upload/invalid_not_in_images.jpg"
    }
    res = client.put(
        "/api/admin/products/60c72b2f9b1d8b2e1c8d0001/thumbnail",
        json=payload,
        headers=headers
    )
    # URL not in images array should return 400
    assert res.status_code == 400
