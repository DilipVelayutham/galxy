"""
seed_categories.py — Module 5 DB seed script
Creates sample category documents with ai_prompt_template for local testing.

Run: python seed_categories.py
Requires MONGO_URI in .env (defaults to mongodb://localhost:27017/galxy).
"""
from dotenv import load_dotenv
load_dotenv()

from app.db import get_db
from app.models.ai_generation import ensure_indexes
from datetime import datetime, timezone


def seed():
    db = get_db()
    categories_col = db["categories"]

    sample_categories = [
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
                    "affects_ai_preview": False,   # excluded from AI prompt
                    "options": [{"value": "NS-001", "label": "NS-001"}],
                },
            ],
            "created_at": datetime.now(timezone.utc),
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
            ],
            "created_at": datetime.now(timezone.utc),
        },
    ]

    inserted = 0
    for cat in sample_categories:
        existing = categories_col.find_one({"slug": cat["slug"]})
        if existing:
            print(f"  [skip] '{cat['name']}' already exists.")
        else:
            categories_col.insert_one(cat)
            print(f"  [ok]   Inserted '{cat['name']}'.")
            inserted += 1

    # Ensure ai_generations indexes
    ensure_indexes()
    print(f"\nSeeded {inserted} new categories. ai_generations indexes ensured.")


if __name__ == "__main__":
    print("Seeding Module 5 test data...")
    seed()
    print("Done.")
