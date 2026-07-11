from datetime import datetime, timezone
import logging
from app.db import get_db

logger = logging.getLogger(__name__)

def get_section(section):
    """
    Retrieves a single site content document for the specified section.
    
    Returns:
        dict or None: The matching document, or None if not found.
    """
    db = get_db()
    return db['site_content'].find_one({"section": section})

def get_bulk(sections):
    """
    Retrieves site content in bulk for a list of sections.
    
    Args:
        sections (list of str): The list of section names.
        
    Returns:
        dict: A mapping of section -> content (e.g. {"hero": {...}, "footer": {...}})
    """
    db = get_db()
    cursor = db['site_content'].find({"section": {"$in": sections}})
    
    bulk_data = {}
    for doc in cursor:
        section_name = doc["section"]
        bulk_data[section_name] = doc.get("content", {})
        
    return bulk_data

def update_section(section, content, admin_user_id):
    """
    Updates the content of a section. This is a full replace of the content dictionary.
    
    Args:
        section (str): The section name.
        content (dict): The new content dictionary.
        admin_user_id (str): The ID of the admin who updated the content.
        
    Returns:
        dict: The updated document.
    """
    db = get_db()
    
    # Define update payload
    now = datetime.now(timezone.utc)
    update_data = {
        "section": section,
        "content": content,
        "updated_at": now,
        "updated_by": admin_user_id
    }
    
    # We use upsert=True since a section might be seeded or initialized on-the-fly.
    # Note: section is unique via unique index constraint, so this is safe and idempotent.
    db['site_content'].update_one(
        {"section": section},
        {"$set": update_data},
        upsert=True
    )
    
    return db['site_content'].find_one({"section": section})
