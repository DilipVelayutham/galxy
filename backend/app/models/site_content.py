import logging
from pymongo import ASCENDING

logger = logging.getLogger(__name__)

# Section 3.1: site_content collection representation and helper keys.
# Schema details:
# {
#   "_id": ObjectId,
#   "section": "hero | about | footer | contact | seo_home | social_links",
#   "content": { ... per-section content },
#   "updated_at": datetime (in UTC),
#   "updated_by": "admin_user_id"
# }

def ensure_indexes():
    """Ensures unique index constraint on the section field in the site_content collection."""
    try:
        from app.db import Database
        db = Database.get_db()
        db['site_content'].create_index(
            [("section", ASCENDING)],
            unique=True,
            name="unique_section_constraint"
        )
        logger.info("Successfully ensured unique index on site_content.section")
    except Exception as e:
        logger.error(f"Error initializing indexes for site_content: {e}")
        raise e
