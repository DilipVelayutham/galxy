import os
import mongomock
from unittest.mock import patch
import cloudinary.uploader
from app.database import db_conn
from app import create_app
from bson import ObjectId
from datetime import datetime, timezone

# Mock Cloudinary SDK uploader calls
def mock_upload(file_stream, **kwargs):
    print("Mock Cloudinary: Intercepted upload call.")
    # Extract folder/name to build a structured public ID
    folder = kwargs.get("folder", "galxy/products")
    # Return simulated success dictionary
    return {
        "secure_url": "https://res.cloudinary.com/v6m2kkn9/image/upload/sample_uploaded.jpg",
        "public_id": f"{folder}/sample_uploaded"
    }

def mock_destroy(public_id, **kwargs):
    print(f"Mock Cloudinary: Intercepted destroy call for {public_id}.")
    return {"result": "ok"}

# Apply the stub immediately
cloudinary.uploader.upload = mock_upload
cloudinary.uploader.destroy = mock_destroy

def mock_init_app(self, app):
    print("Mocking MongoDB connection using mongomock...")
    mock_client = mongomock.MongoClient()
    self.client = mock_client
    self.db = mock_client["galxy_mock_db"]
    
    # Mock database ping command
    original_command = self.db.command
    def mock_command(cmd, *args, **kwargs):
        if cmd == "ping":
            return {"ok": 1.0}
        try:
            return original_command(cmd, *args, **kwargs)
        except Exception:
            return {"ok": 1.0}
            
    self.db.command = mock_command
    self.create_indexes()
    
    # Seed the mock database
    seed_mock_db(self.db)

def seed_mock_db(db):
    print("Seeding mock database...")
    # Drop existing collections if any
    db.categories.drop()
    db.products.drop()
    
    # Categories
    neon_cat_id = ObjectId("6686b245e4b06825c5d082f4")
    quilling_cat_id = ObjectId("6686b245e4b06825c5d082f5")
    
    categories = [
        {
            "_id": neon_cat_id,
            "name": "Neon Name Boards",
            "slug": "neon-name-boards",
            "description": "Bespoke custom glowing neon signage boards.",
            "cover_image": "https://res.cloudinary.com/v6m2kkn9/image/upload/sample.jpg",
            "banner_image": "https://res.cloudinary.com/v6m2kkn9/image/upload/sample.jpg",
            "display_order": 1,
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
                    "required": True,
                    "display_order": 1
                },
                {
                    "key": "color",
                    "label": "Neon Glow Color",
                    "type": "color_swatch",
                    "options": [
                        { "value": "blue", "label": "Electric Blue", "price_delta": 0 },
                        { "value": "pink", "label": "Hot Pink", "price_delta": 100 },
                        { "value": "violet", "label": "Soft Violet", "price_delta": 120 }
                    ],
                    "required": True,
                    "display_order": 2
                },
                {
                    "key": "backing",
                    "label": "Acrylic Backing Type",
                    "type": "select",
                    "options": [
                        { "value": "clear", "label": "Clear Cut acrylic", "price_delta": 0 },
                        { "value": "black", "label": "Solid Black Glossy", "price_delta": 200 }
                    ],
                    "required": False,
                    "display_order": 3
                }
            ],
            "accent_color": "#18E7FF",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "_id": quilling_cat_id,
            "name": "Quilling Art",
            "slug": "quilling-art",
            "description": "Exquisite paper-rolled quilling wall decor frames.",
            "cover_image": "https://res.cloudinary.com/v6m2kkn9/image/upload/sample.jpg",
            "banner_image": "https://res.cloudinary.com/v6m2kkn9/image/upload/sample.jpg",
            "display_order": 2,
            "is_active": True,
            "attribute_schema": [
                {
                    "key": "frame_size",
                    "label": "Frame Outer Dimension",
                    "type": "select",
                    "options": [
                        { "value": "A4", "label": "A4 size frame", "price_delta": 0 },
                        { "value": "A3", "label": "A3 premium size frame", "price_delta": 400 }
                    ],
                    "required": True,
                    "display_order": 1
                },
                {
                    "key": "base_color",
                    "label": "Background Cardstock Color",
                    "type": "color_swatch",
                    "options": [
                        { "value": "white", "label": "Midnight White", "price_delta": 0 },
                        { "value": "black", "label": "Charcoal Black", "price_delta": 50 }
                    ],
                    "required": True,
                    "display_order": 2
                },
                {
                    "key": "flower_density",
                    "label": "Flower Density",
                    "type": "slider",
                    "min": 1.0,
                    "max": 10.0,
                    "step": 1.0,
                    "required": False,
                    "display_order": 3
                }
            ],
            "accent_color": "#FF2E8A",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    db.categories.insert_many(categories)
    print("Categories seeded.")
    
    # Products
    products = [
        {
            "_id": ObjectId("6686b245e4b06825c5d082f6"),
            "category_id": neon_cat_id,
            "category_slug": "neon-name-boards",
            "title": "Dream Big Cursive Neon Sign",
            "slug": "dream-big-cursive-neon-sign",
            "type": "pre_designed",
            "base_price": 1499.0,
            "images": [
                {
                    "url": "https://res.cloudinary.com/v6m2kkn9/image/upload/sample_neon1.jpg",
                    "public_id": "galxy/products/sample_neon1"
                }
            ],
            "thumbnail": "https://res.cloudinary.com/v6m2kkn9/image/upload/sample_neon1.jpg",
            "description": "Get inspired daily with our classic 'Dream Big' cursive hand-styled neon name board.",
            "specifications": {
                "material": "Flex LED & Acrylic Base",
                "power": "12V adapter included",
                "avg_production_days": 5
            },
            "default_attributes": {
                "font": "cursive",
                "color": "pink",
                "backing": "clear"
            },
            "stock_status": "made_to_order",
            "tags": ["bestseller", "new", "gifting"],
            "is_featured": True,
            "is_active": True,
            "views": 42,
            "rating_avg": 4.8,
            "rating_count": 5,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "_id": ObjectId("6686b245e4b06825c5d082f7"),
            "category_id": neon_cat_id,
            "category_slug": "neon-name-boards",
            "title": "Custom Neon Board",
            "slug": "custom-neon-board",
            "type": "fully_custom",
            "base_price": 999.0,
            "images": [
                {
                    "url": "https://res.cloudinary.com/v6m2kkn9/image/upload/sample_neon_custom.jpg",
                    "public_id": "galxy/products/sample_neon_custom"
                }
            ],
            "thumbnail": "https://res.cloudinary.com/v6m2kkn9/image/upload/sample_neon_custom.jpg",
            "description": "Design your own custom neon board. Enter your text and select your options below.",
            "specifications": {
                "material": "High grade LED Neon",
                "power": "12V Adapter with dimming plug",
                "avg_production_days": 7
            },
            "default_attributes": {
                "font": "bold",
                "color": "blue",
                "backing": "clear"
            },
            "stock_status": "made_to_order",
            "tags": ["custom"],
            "is_featured": False,
            "is_active": True,
            "views": 150,
            "rating_avg": 4.9,
            "rating_count": 12,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    db.products.insert_many(products)
    print("Products seeded.")

# Apply patch before constructing app
with patch("app.database.DatabaseConnection.init_app", mock_init_app):
    app = create_app()

if __name__ == "__main__":
    print("Starting Mock Server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=False)
