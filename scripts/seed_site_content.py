import sys
import os
import logging
from datetime import datetime, timezone

# Add the root directory to path to enable app imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from app.db import Database
from app.utils.content_schema_validator import validate_content, SECTION_ENUM

DEFAULT_SEEDS = {
    "hero": {
        "headline": "Welcome to GALXY Studio",
        "subheadline": "Custom Lighting & Craft Studio",
        "background_video_url": "https://res.cloudinary.com/cipbjrym/video/upload/v1/hero_bg.mp4",
        "background_image_url": "https://res.cloudinary.com/cipbjrym/image/upload/v1/hero_bg.jpg",
        "cta_text": "Explore Collection",
        "cta_link": "/shop"
    },
    "about": {
        "title": "About GALXY Studio",
        "body_text": "We design and build bespoke custom lighting elements and glass crafts that bring warmth and character to your homes and commercial spaces. Our works are crafted by hand in our local workshop using recycled materials and energy-efficient LED modules.",
        "images": [
            "https://res.cloudinary.com/cipbjrym/image/upload/v1/workshop_1.jpg",
            "https://res.cloudinary.com/cipbjrym/image/upload/v1/workshop_2.jpg"
        ],
        "founder_name": "Asil",
        "founder_photo": "https://res.cloudinary.com/cipbjrym/image/upload/v1/founder.jpg"
    },
    "footer": {
        "tagline": "GALXY — Crafting Light from Dust",
        "quick_links": [
            {"label": "About", "url": "/about"},
            {"label": "Contact Us", "url": "/contact"}
        ],
        "business_hours": "Mon - Fri: 9:00 AM - 6:00 PM, Sat: 10:00 AM - 4:00 PM"
    },
    "contact": {
        "phone": "+919876543210",
        "whatsapp_number": "+919876543210",
        "email": "contact@galxystudio.com",
        "address": "123 Nebula Way, Starlight District, Chennai - 600001",
        "map_embed_url": "https://res.cloudinary.com/cipbjrym/image/upload/v1/map_location"
    },
    "seo_home": {
        "meta_title": "GALXY — Custom Lighting & Handmade Glass Craft",
        "meta_description": "Explore beautiful, handmade bespoke lights, pendants, and custom glass creations at GALXY Studio. Built locally with premium sustainable materials.",
        "og_image": "https://res.cloudinary.com/cipbjrym/image/upload/v1/og_banner.jpg"
    },
    "social_links": {
        "instagram": "https://instagram.com/galxystudio",
        "facebook": "https://facebook.com/galxystudio",
        "youtube": "https://youtube.com/c/galxystudio"
    }
}

def seed_database():
    """Seeds the MongoDB database collection site_content idempotently."""
    logger.info("Initializing DB connection and indexes...")
    Database.init_db()
    db = Database.get_db()
    collection = db['site_content']
    
    success_count = 0
    now = datetime.now(timezone.utc)
    
    for section, content in DEFAULT_SEEDS.items():
        logger.info(f"Validating defaults for section: '{section}'...")
        is_valid, errors = validate_content(section, content)
        if not is_valid:
            logger.error(f"Seed validation failed for '{section}': {errors}")
            continue
            
        logger.info(f"Upserting section: '{section}'...")
        doc = {
            "section": section,
            "content": content,
            "updated_at": now,
            "updated_by": "system_seed"
        }
        
        # Idempotent upsert by section
        collection.update_one(
            {"section": section},
            {"$set": doc},
            upsert=True
        )
        success_count += 1
        
    logger.info(f"Database seeding complete. Successfully seeded {success_count}/{len(DEFAULT_SEEDS)} sections.")

if __name__ == "__main__":
    seed_database()
