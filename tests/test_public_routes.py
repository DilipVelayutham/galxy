import pytest
from bson import ObjectId
from datetime import datetime, timezone

@pytest.fixture(autouse=True)
def setup_categories_and_products(db):
    """
    Clears the test database and seeds it with mock categories and products for testing.
    """
    db.categories.drop()
    db.products.drop()
    
    # Seed Categories
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
                }
            ],
            "accent_color": "#18E7FF"
        },
        {
            "_id": ObjectId("60c72b2f9b1d8b2e1c8d5679"),
            "name": "Quilling Art",
            "slug": "quilling-art",
            "is_active": True,
            "attribute_schema": [],
            "accent_color": "#FF2E8A"
        }
    ])
    
    # Seed Products
    db.products.insert_many([
        {
            "category_id": ObjectId("60c72b2f9b1d8b2e1c8d5678"),
            "category_slug": "neon-name-boards",
            "title": "Neon Light 1",
            "slug": "neon-light-1",
            "type": "pre_designed",
            "base_price": 1000.0,
            "images": [{"url": "https://res.cloudinary.com/v6m2kkn9/image/upload/image1.jpg", "public_id": "img1"}],
            "thumbnail": "https://res.cloudinary.com/v6m2kkn9/image/upload/image1.jpg",
            "description": "Awesome glowing neon light board.",
            "specifications": {"material": "LED Neon"},
            "default_attributes": {"font": "cursive"},
            "stock_status": "in_stock",
            "tags": ["bestseller", "glow"],
            "is_featured": True,
            "is_active": True,
            "views": 10,
            "rating_avg": 4.5,
            "rating_count": 1,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "category_id": ObjectId("60c72b2f9b1d8b2e1c8d5678"),
            "category_slug": "neon-name-boards",
            "title": "Neon Light 2",
            "slug": "neon-light-2",
            "type": "fully_custom",
            "base_price": 2000.0,
            "images": [],
            "thumbnail": None,
            "description": "Customizable neon name board.",
            "specifications": {},
            "default_attributes": {"font": "bold"},
            "stock_status": "made_to_order",
            "tags": ["custom"],
            "is_featured": False,
            "is_active": True,
            "views": 5,
            "rating_avg": 0.0,
            "rating_count": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "category_id": ObjectId("60c72b2f9b1d8b2e1c8d5679"),
            "category_slug": "quilling-art",
            "title": "Quilling Flower Frame",
            "slug": "quilling-flower-frame",
            "type": "pre_designed",
            "base_price": 1500.0,
            "images": [{"url": "https://res.cloudinary.com/v6m2kkn9/image/upload/image2.jpg", "public_id": "img2"}],
            "thumbnail": "https://res.cloudinary.com/v6m2kkn9/image/upload/image2.jpg",
            "description": "Rolled paper flower frame.",
            "specifications": {},
            "default_attributes": {},
            "stock_status": "out_of_stock",
            "tags": ["gifting"],
            "is_featured": True,
            "is_active": False, # Inactive
            "views": 2,
            "rating_avg": 4.0,
            "rating_count": 2,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ])

def test_get_products_public(client):
    """
    Verifies public listings only contain active products and format matches lightweight shape.
    """
    response = client.get("/api/products")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    data = json_data["data"]
    
    # 2 active, 1 inactive
    assert len(data) == 2
    
    for prod in data:
        # Check standard fields presence
        assert "_id" in prod
        assert "title" in prod
        assert "slug" in prod
        assert "category_slug" in prod
        assert "thumbnail" in prod
        assert "base_price" in prod
        assert "stock_status" in prod
        assert "rating_avg" in prod
        assert "is_featured" in prod
        
        # Check heavy fields omission
        assert "description" not in prod
        assert "images" not in prod
        assert "default_attributes" not in prod
        assert "specifications" not in prod

def test_get_products_filters(client):
    """
    Tests query parameters filtering capabilities.
    """
    # Category slug filtering
    res = client.get("/api/products?category=neon-name-boards")
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 2
    
    # Featured filtering
    res = client.get("/api/products?featured=true")
    assert len(res.get_json()["data"]) == 1 # Only Neon Light 1 (Neon Light 2 is False, Quilling is Inactive)
    
    # Price range filtering
    res = client.get("/api/products?min_price=1200&max_price=2500")
    data = res.get_json()["data"]
    assert len(data) == 1
    assert data[0]["title"] == "Neon Light 2"

def test_get_product_by_slug_public(client, db):
    """
    Verifies that public product details are fetched correctly with category details nested.
    """
    response = client.get("/api/products/neon-light-1")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    
    # Check data fields
    product = json_data["data"]
    assert product["title"] == "Neon Light 1"
    assert "description" in product
    assert "images" in product
    
    # Check category nesting
    assert "category" in product
    assert product["category"]["name"] == "Neon Name Boards"
    assert len(product["category"]["attribute_schema"]) == 1
    
    # Check views side-effect
    refreshed_prod = db.products.find_one({"slug": "neon-light-1"})
    assert refreshed_prod["views"] == 11

def test_get_product_by_slug_not_found(client):
    """
    Non-existent slug or inactive product slug should return 404.
    """
    # Non-existent
    response = client.get("/api/products/missing-slug")
    assert response.status_code == 404
    
    # Inactive product
    response = client.get("/api/products/quilling-flower-frame")
    assert response.status_code == 404

def test_search_products(client):
    """
    Tests full-text search endpoint.
    """
    # Valid query
    response = client.get("/api/products/search?q=neon")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 2 # Neon Light 1 and Neon Light 2
    
    # Short query should fail with 400
    response = client.get("/api/products/search?q=x")
    assert response.status_code == 400
    assert response.get_json()["success"] is False
