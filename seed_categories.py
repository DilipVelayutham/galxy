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
        "ai_prompt_template": "A realistic professional product photo of a custom neon sign spelling \"{custom_text}\", in {color} color, {font} font style, {chain} hanging chain, mounted on a dark brick wall with soft ambient glow, studio lighting, high detail, no watermark",
        "attributes": [
            {
                "key": "font",
                "name": "Font Style",
                "affects_ai_preview": True,
                "options": [
                    {"code": "cursive", "label": "Cursive neon script"},
                    {"code": "serif", "label": "Classic serif style"},
                    {"code": "sans-serif", "label": "Clean sans-serif"}
                ]
            },
            {
                "key": "color",
                "name": "Neon Color",
                "affects_ai_preview": True,
                "options": [
                    {"code": "blue", "label": "electric blue"},
                    {"code": "pink", "label": "hot pink"},
                    {"code": "green", "label": "vibrant lime green"}
                ]
            },
            {
                "key": "chain",
                "name": "Hanging Chain",
                "affects_ai_preview": True,
                "options": [
                    {"code": "yes", "label": "with heavy metal"},
                    {"code": "no", "label": "without any"}
                ]
            },
            {
                "key": "size",
                "name": "Sign Size",
                "affects_ai_preview": False,  # Should be ignored by prompt builder
                "options": [
                    {"code": "small", "label": "20cm"},
                    {"code": "medium", "label": "40cm"},
                    {"code": "large", "label": "60cm"}
                ]
            },
            {
                "key": "custom_text",
                "name": "Custom Sign Text",
                "type": "text",
                "affects_ai_preview": True
            }
        ]
    }
    
    categories.replace_one({"_id": neon_sign_id}, category_doc, upsert=True)
    print(f"Successfully seeded category 'Neon Sign' with ID: {neon_sign_id}")

if __name__ == "__main__":
    seed()
