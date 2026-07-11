import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

def seed_db():
    load_dotenv()
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME", "galxy_db")
    
    if not uri:
        print("Error: MONGO_URI is not set in environment.")
        return
        
    db = None
    print(f"Connecting to database '{db_name}'...")
    try:
        # Use a short selection timeout of 5 seconds to fail fast
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        
        # Test connection explicitly
        client.admin.command('ping')
        
        # 1. Drop existing products and categories
        print("Dropping categories and products collections...")
        db.categories.drop()
        db.products.drop()
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        print("\n" + "="*80)
        print("[DATABASE CONNECTION ERROR]")
        print("Failed to connect to the MongoDB Atlas cluster.")
        print(f"Details: {e}")
        print("\nThis SSL handshake / selection timeout error is most commonly caused by")
        print("MongoDB Atlas Network Access (IP Whitelisting) restrictions.")
        print("\nTo resolve this:")
        print("1. Log in to your MongoDB Atlas Dashboard.")
        print("2. Navigate to 'Network Access' under the Security section.")
        print("3. Click 'Add IP Address'.")
        print("4. Add your current public IP address, or enter '0.0.0.0/0' to temporarily")
        print("   allow access from anywhere for development/testing.")
        print("="*80 + "\n")
        return

    
    # 2. Re-create indexes
    print("Re-creating product indexes...")
    from pymongo import ASCENDING, TEXT
    db.products.create_index("slug", unique=True)
    db.products.create_index("category_id")
    db.products.create_index("tags")
    db.products.create_index([("is_active", ASCENDING), ("is_featured", ASCENDING)])
    db.products.create_index([
        ("title", TEXT),
        ("description", TEXT)
    ], weights={"title": 10, "description": 2}, name="product_search_text_index")
    print("MongoDB indexes created successfully.")
    
    # 3. Seed Categories (representing Module 2 collections locally for validation)
    print("Seeding categories...")
    neon_cat_id = ObjectId()
    quilling_cat_id = ObjectId()
    
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
    print("Categories seeded successfully.")
    
    # 4. Seed Products
    print("Seeding products...")
    products = [
        {
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
                "material": "Flex LED Neon & Acrylic Base",
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
        },
        {
            "category_id": quilling_cat_id,
            "category_slug": "quilling-art",
            "title": "Floral Anniversary Quilling Art",
            "slug": "floral-anniversary-quilling-art",
            "type": "pre_designed",
            "base_price": 2499.0,
            "images": [
                {
                    "url": "https://res.cloudinary.com/v6m2kkn9/image/upload/sample_quill1.jpg",
                    "public_id": "galxy/products/sample_quill1"
                }
            ],
            "thumbnail": "https://res.cloudinary.com/v6m2kkn9/image/upload/sample_quill1.jpg",
            "description": "Handcrafted rolled-paper typography frame, perfect for weddings and anniversaries.",
            "specifications": {
                "material": "Acid-free archival paper & wooden shadowbox",
                "avg_production_days": 10
            },
            "default_attributes": {
                "frame_size": "A4",
                "base_color": "white",
                "flower_density": 5.0
            },
            "stock_status": "in_stock",
            "tags": ["anniversary", "gifting"],
            "is_featured": True,
            "is_active": True,
            "views": 28,
            "rating_avg": 4.5,
            "rating_count": 2,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    db.products.insert_many(products)
    print("Products seeded successfully.")
    print(f"Database '{db_name}' seeded successfully!")

if __name__ == "__main__":
    seed_db()
