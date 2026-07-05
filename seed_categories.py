import os
from pymongo import MongoClient
from bson import ObjectId

def seed():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/galxy")
    client = MongoClient(mongo_uri)
    db = client.get_default_database()
    
    categories = db["categories"]
    
    # Consistent ID for testing
    neon_sign_id = ObjectId("66851234af504e44a4b8c771")
    
    category_doc = {
        "_id": neon_sign_id,
        "name": "Neon Sign",
        "ai_prompt_template": "A realistic professional product photo of a custom neon sign spelling \"{custom_text}\", in {color} color, {font} font style, {mounting} hanging, mounted on a dark background with soft ambient glow, studio lighting, high detail, no watermark, no text overlay",
        "attributes": [
            {
                "key": "custom_text",
                "name": "Custom Neon Text",
                "type": "text",
                "affects_ai_preview": True,
                "default_value": "Dream Big"
            },
            {
                "key": "color",
                "name": "Neon Glow Color",
                "type": "radio",
                "affects_ai_preview": True,
                "options": [
                    {"code": "blue", "label": "Electric Blue"},
                    {"code": "pink", "label": "Neon Pink"},
                    {"code": "gold", "label": "Warm Gold"}
                ]
            },
            {
                "key": "font",
                "name": "Font Style",
                "type": "select",
                "affects_ai_preview": True,
                "options": [
                    {"code": "cursive", "label": "Cursive"}
                ]
            },
            {
                "key": "mounting",
                "name": "Mounting Options",
                "type": "radio",
                "affects_ai_preview": True,
                "options": [
                    {"code": "chain", "label": "Chain"}
                ]
            },
            {
                "key": "backing",
                "name": "Backing Board Material",
                "type": "radio",
                "affects_ai_preview": False,
                "options": [
                    {"code": "acrylic", "label": "Acrylic"}
                ]
            }
        ]
    }
    
    categories.replace_one({"_id": neon_sign_id}, category_doc, upsert=True)
    print(f"Successfully seeded category 'Neon Sign' with ID: {neon_sign_id}")

if __name__ == "__main__":
    seed()
