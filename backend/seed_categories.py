import os
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://lti_platform:open123%21%40%23@ltiplat.hf8dbrx.mongodb.net/?appName=ltiplat")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "lti_hub_db")

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
categories = db["m5_categories"]

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
                "affects_ai_preview": False,  # Excluded from prompt building
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
                "affects_ai_preview": False,  # Excluded from prompt building
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
                "options": []  # Free text input
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
    }
]

def seed():
    print(f"Connecting to database: '{MONGO_DB_NAME}'...")
    count = 0
    for cat in mock_categories:
        # Upsert category based on category_id
        res = categories.update_one(
            {"category_id": cat["category_id"]},
            {"$set": cat},
            upsert=True
        )
        if res.upserted_id:
            print(f"Created category: {cat['name']} (ID: {cat['category_id']})")
        else:
            print(f"Updated category: {cat['name']} (ID: {cat['category_id']})")
        count += 1
    print(f"Seeding completed successfully. {count} categories written.")

if __name__ == "__main__":
    seed()
