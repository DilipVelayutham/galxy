"""
seed_categories.py — Module 5 DB seed script
Creates sample category documents with ai_prompt_template for local testing.

Run: python seed_categories.py
Requires MONGO_URI in .env.
"""
import os
import pymongo
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# Attempt to import app-specific helpers, but design fallbacks if they are not available or raise SyntaxError due to other conflicts
try:
    from app.db import get_db
    from app.models.ai_generation import ensure_indexes
    has_app = True
except Exception:
    has_app = False

# We combine the category schemas to be compatible with both attribute_schema and attributes
mock_categories = [
    {
        "category_id": "custom_apparels",
        "slug": "custom-apparels",
        "name": "Custom Apparels",
        "description": "Customize your own high-quality t-shirts, hoodies, and sweatshirts.",
        "cover_image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518",
        "banner_image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518",
        "display_order": 1,
        "is_active": True,
        "ai_prompt_template": "A high-quality studio product photo of a custom {color} {style} displayed on a clean white background. In the center of the garment, the words '{custom_text}' are printed in a clean minimalist font.",
        "attribute_schema": [
            {
                "key": "style",
                "label": "Garment Style",
                "type": "select",
                "required": True,
                "affects_ai_preview": True,
                "display_order": 1,
                "options": [
                    {"value": "tshirt", "label": "T-Shirt", "price_delta": 0},
                    {"value": "hoodie", "label": "Hoodie", "price_delta": 500},
                    {"value": "sweatshirt", "label": "Sweatshirt", "price_delta": 300}
                ]
            },
            {
                "key": "color",
                "label": "Fabric Color",
                "type": "color_swatch",
                "required": True,
                "affects_ai_preview": True,
                "display_order": 2,
                "options": [
                    {"value": "black", "label": "Black", "price_delta": 0},
                    {"value": "white", "label": "White", "price_delta": 0},
                    {"value": "red", "label": "Red", "price_delta": 50},
                    {"value": "navy", "label": "Navy Blue", "price_delta": 50}
                ]
            },
            {
                "key": "fabric",
                "label": "Fabric Weight",
                "type": "select",
                "required": False,
                "affects_ai_preview": False,
                "display_order": 3,
                "options": [
                    {"value": "standard", "label": "Standard Cotton (180 GSM)", "price_delta": 0},
                    {"value": "heavy", "label": "Heavyweight Cotton (240 GSM)", "price_delta": 150}
                ]
            },
            {
                "key": "size",
                "label": "Size",
                "type": "select",
                "required": True,
                "affects_ai_preview": False,
                "display_order": 4,
                "options": [
                    {"value": "s", "label": "Small", "price_delta": 0},
                    {"value": "m", "label": "Medium", "price_delta": 0},
                    {"value": "l", "label": "Large", "price_delta": 0},
                    {"value": "xl", "label": "Extra Large", "price_delta": 50}
                ]
            },
            {
                "key": "custom_text",
                "label": "Custom Text/Quote",
                "type": "text_input",
                "required": True,
                "affects_ai_preview": True,
                "display_order": 5,
                "options": []
            }
        ]
    },
    {
        "category_id": "custom_drinkware",
        "slug": "custom-drinkware",
        "name": "Custom Drinkware",
        "description": "Design custom ceramic mugs and stainless steel travel tumblers.",
        "cover_image": "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d",
        "banner_image": "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d",
        "display_order": 2,
        "is_active": True,
        "ai_prompt_template": "A professional studio shot of a {material} mug in {color} color. On the front of the mug, the text '{custom_text}' is clearly engraved/printed. Soft lighting, modern aesthetic.",
        "attribute_schema": [
            {
                "key": "material",
                "label": "Material",
                "type": "select",
                "required": True,
                "affects_ai_preview": True,
                "display_order": 1,
                "options": [
                    {"value": "ceramic", "label": "Ceramic", "price_delta": 0},
                    {"value": "steel", "label": "Stainless Steel", "price_delta": 250}
                ]
            },
            {
                "key": "color",
                "label": "Mug Color",
                "type": "color_swatch",
                "required": True,
                "affects_ai_preview": True,
                "display_order": 2,
                "options": [
                    {"value": "matte_black", "label": "Matte Black", "price_delta": 0},
                    {"value": "glossy_white", "label": "Glossy White", "price_delta": 0},
                    {"value": "emerald_green", "label": "Emerald Green", "price_delta": 80}
                ]
            },
            {
                "key": "size",
                "label": "Capacity",
                "type": "select",
                "required": True,
                "affects_ai_preview": False,
                "display_order": 3,
                "options": [
                    {"value": "11oz", "label": "11 oz (325ml)", "price_delta": 0},
                    {"value": "15oz", "label": "15 oz (440ml)", "price_delta": 80}
                ]
            },
            {
                "key": "custom_text",
                "label": "Printed Text",
                "type": "text_input",
                "required": True,
                "affects_ai_preview": True,
                "display_order": 4,
                "options": []
            }
        ]
    },
    {
        "category_id": "custom_phone_cases",
        "slug": "custom-phone-cases",
        "name": "Custom Phone Cases",
        "description": "Design custom phone cases for iPhone and Samsung models.",
        "cover_image": "https://images.unsplash.com/photo-1603302576837-37561b2e2302",
        "banner_image": "https://images.unsplash.com/photo-1603302576837-37561b2e2302",
        "display_order": 3,
        "is_active": True,
        "ai_prompt_template": "A sleek {case_material} phone case in {color} color on a solid grey background. The back of the phone case features the custom text '{custom_text}' printed in a beautiful metallic gold font.",
        "attribute_schema": [
            {
                "key": "phone_model",
                "label": "Phone Model",
                "type": "select",
                "required": True,
                "affects_ai_preview": False,
                "display_order": 1,
                "options": [
                    {"value": "iphone_15", "label": "iPhone 15 Pro", "price_delta": 0},
                    {"value": "iphone_15_pro_max", "label": "iPhone 15 Pro Max", "price_delta": 100},
                    {"value": "samsung_s24", "label": "Samsung Galaxy S24", "price_delta": 0}
                ]
            },
            {
                "key": "case_material",
                "label": "Case Type",
                "type": "select",
                "required": True,
                "affects_ai_preview": True,
                "display_order": 2,
                "options": [
                    {"value": "silicone", "label": "Silicone Case", "price_delta": 0},
                    {"value": "clear", "label": "Clear Case", "price_delta": 0},
                    {"value": "tough", "label": "Armor Tough Case", "price_delta": 200}
                ]
            },
            {
                "key": "color",
                "label": "Primary Color",
                "type": "color_swatch",
                "required": True,
                "affects_ai_preview": True,
                "display_order": 3,
                "options": [
                    {"value": "midnight", "label": "Midnight Black", "price_delta": 0},
                    {"value": "lavender", "label": "Lavender", "price_delta": 0},
                    {"value": "crimson", "label": "Crimson Red", "price_delta": 50}
                ]
            },
            {
                "key": "custom_text",
                "label": "Engraved Monogram",
                "type": "text_input",
                "required": True,
                "affects_ai_preview": True,
                "display_order": 4,
                "options": []
            }
        ]
    },
    {
        "name": "Neon Sign",
        "slug": "neon-sign",
        "ai_prompt_template": (
            'A realistic professional product photo of a custom Neon Sign spelling '
            '"{custom_text}", in {color} color, {font} font style, '
            "{chain} hanging chain, mounted on a dark background with soft "
            "ambient glow, studio lighting, high detail, no watermark, no text overlay"
        ),
        "attributes": [
            {
                "key": "custom_text",
                "label": "Custom Text",
                "type": "text_input",
                "required": True,
                "affects_ai_preview": True,
            },
            {
                "key": "color",
                "label": "Neon Color",
                "type": "option",
                "required": True,
                "affects_ai_preview": True,
                "options": [
                    {"value": "blue", "label": "Blue"},
                    {"value": "red", "label": "Red"},
                    {"value": "warm_white", "label": "Warm White"},
                    {"value": "pink", "label": "Pink"},
                    {"value": "green", "label": "Green"},
                ],
            },
            {
                "key": "font",
                "label": "Font Style",
                "type": "option",
                "required": True,
                "affects_ai_preview": True,
                "options": [
                    {"value": "cursive_v2", "label": "Cursive"},
                    {"value": "bold_v1", "label": "Bold"},
                    {"value": "script_v3", "label": "Script"},
                    {"value": "serif_v1", "label": "Serif"},
                ],
            },
            {
                "key": "chain",
                "label": "Hanging Chain",
                "type": "option",
                "required": False,
                "affects_ai_preview": True,
                "options": [
                    {"value": "with_chain", "label": "with"},
                    {"value": "no_chain", "label": "without"},
                ],
            },
            {
                "key": "sku_ref",
                "label": "Internal SKU",
                "type": "option",
                "required": False,
                "affects_ai_preview": False,
                "options": [{"value": "NS-001", "label": "NS-001"}],
            },
        ]
    },
    {
        "name": "LED Letter Sign",
        "slug": "led-letter-sign",
        "ai_prompt_template": (
            "A high-quality studio photograph of a {size} LED letter sign "
            "with {finish} finish, lit in {color} light, placed on a "
            "minimalist white shelf, product photography style"
        ),
        "attributes": [
            {
                "key": "size",
                "label": "Size",
                "type": "option",
                "required": True,
                "affects_ai_preview": True,
                "options": [
                    {"value": "small_30cm", "label": "small (30cm)"},
                    {"value": "medium_60cm", "label": "medium (60cm)"},
                    {"value": "large_90cm", "label": "large (90cm)"},
                ],
            },
            {
                "key": "finish",
                "label": "Finish",
                "type": "option",
                "required": True,
                "affects_ai_preview": True,
                "options": [
                    {"value": "matte_black", "label": "matte black"},
                    {"value": "chrome", "label": "chrome"},
                    {"value": "rose_gold", "label": "rose gold"},
                ],
            },
            {
                "key": "color",
                "label": "LED Color",
                "type": "option",
                "required": True,
                "affects_ai_preview": True,
                "options": [
                    {"value": "warm_white", "label": "warm white"},
                    {"value": "cool_white", "label": "cool white"},
                    {"value": "rgb_multi", "label": "multicolor RGB"},
                ],
            },
        ]
    }
]

def normalize_categories(cats):
    normalized = []
    for cat in cats:
        c = cat.copy()
        
        # Ensure category_id exists
        if "category_id" not in c:
            c["category_id"] = c.get("slug", "").replace("-", "_")
            
        # Ensure slug exists
        if "slug" not in c:
            c["slug"] = c.get("category_id", "").replace("_", "-")
            
        # Synchronize attribute_schema and attributes
        if "attribute_schema" in c and "attributes" not in c:
            c["attributes"] = c["attribute_schema"]
        elif "attributes" in c and "attribute_schema" not in c:
            c["attribute_schema"] = c["attributes"]
            
        # Ensure display_order
        if "display_order" not in c:
            c["display_order"] = 99
            
        # Ensure is_active
        if "is_active" not in c:
            c["is_active"] = True
            
        # Ensure description, cover_image, banner_image
        if "description" not in c:
            c["description"] = f"Design custom {c['name'].lower()} online."
        if "cover_image" not in c:
            c["cover_image"] = "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d"
        if "banner_image" not in c:
            c["banner_image"] = "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d"
            
        # Ensure created_at
        c["created_at"] = datetime.now(timezone.utc)
        
        normalized.append(c)
    return normalized

def seed():
    mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://lti_platform:open123%21%40%23@ltiplat.hf8dbrx.mongodb.net/?appName=ltiplat")
    mongo_db_name = os.getenv("MONGO_DB_NAME", "lti_hub_db")
    
    db = None
    if has_app:
        try:
            db = get_db()
            print("Successfully retrieved database connection via app.db.get_db()")
        except Exception as e:
            print(f"Failed to use app.db.get_db(): {e}")
            
    if db is None:
        try:
            client = pymongo.MongoClient(mongo_uri)
            db = client[mongo_db_name]
            print(f"Connected directly to database: '{mongo_db_name}'")
        except Exception as e:
            print(f"Failed to connect to database directly: {e}")
            return
            
    # Seed both collection names to ensure compatibility with whichever collections the schemas query
    collections = [db["m5_categories"], db["categories"]]
    normalized_cats = normalize_categories(mock_categories)
    
    for col in collections:
        print(f"Seeding collection '{col.name}'...")
        count = 0
        for cat in normalized_cats:
            res = col.update_one(
                {"slug": cat["slug"]},
                {"$set": cat},
                upsert=True
            )
            if res.upserted_id:
                print(f"  Created: {cat['name']} (Slug: {cat['slug']})")
            else:
                print(f"  Updated: {cat['name']} (Slug: {cat['slug']})")
            count += 1
        print(f"Seeding collection '{col.name}' completed. {count} categories written.")
        
    if has_app:
        try:
            ensure_indexes()
            print("Successfully ensured database indexes.")
        except Exception as e:
            print(f"Could not ensure indexes: {e}")

if __name__ == "__main__":
    print("Seeding Module 5 database data...")
    seed()
    print("Done.")
