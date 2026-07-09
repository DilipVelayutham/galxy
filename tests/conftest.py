import pytest
import mongomock
from bson import ObjectId
from app import create_app
from app.db import get_db

@pytest.fixture
def mock_client():
    return mongomock.MongoClient()

@pytest.fixture
def app(mock_client):
    app = create_app(testing=True, mock_client=mock_client)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    return get_db()

@pytest.fixture
def seed_data(db):
    # Clear collections
    db.categories.delete_many({})
    db.products.delete_many({})
    db.carts.delete_many({})
    
    # 1. Seed categories
    category_id = ObjectId()
    category = {
        "_id": category_id,
        "name": "Neon Boards",
        "slug": "neon-boards",
        "attribute_schema": [
            {
                "key": "font",
                "label": "Font Style",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "cursive", "label": "Cursive", "price_delta": 0},
                    {"value": "bold", "label": "Bold", "price_delta": 150}
                ]
            },
            {
                "key": "color",
                "label": "Glow Color",
                "type": "color_swatch",
                "required": True,
                "options": [
                    {"value": "pink", "label": "Magenta Pink", "price_delta": 0},
                    {"value": "blue", "label": "Electric Blue", "price_delta": 100}
                ]
            },
            {
                "key": "size",
                "label": "Size (cm)",
                "type": "slider",
                "required": False,
                "min": 10,
                "max": 100
            }
        ]
    }
    db.categories.insert_one(category)
    
    # 2. Seed products
    product_active_id = ObjectId()
    product_active = {
        "_id": product_active_id,
        "category_id": category_id,
        "title": "Custom Neon Sign",
        "thumbnail": "http://res.cloudinary.com/test/neon.jpg",
        "base_price": 1500,
        "is_active": True
    }
    db.products.insert_one(product_active)
    
    product_inactive_id = ObjectId()
    product_inactive = {
        "_id": product_inactive_id,
        "category_id": category_id,
        "title": "Outdated Neon Sign",
        "thumbnail": "http://res.cloudinary.com/test/outdated.jpg",
        "base_price": 1200,
        "is_active": False
    }
    db.products.insert_one(product_inactive)
    
    return {
        "category_id": category_id,
        "product_active_id": product_active_id,
        "product_inactive_id": product_inactive_id
    }
