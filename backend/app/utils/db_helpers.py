"""
db_helpers.py — Module 5 DB utility helpers
Shared DB query helpers used across services.
"""
from bson import ObjectId
from app.db import get_db


def get_category_by_id(category_id: str) -> dict | None:
    """
    Fetch a category document from Module 2's categories collection.
    Returns None if not found or if category_id is invalid.
    """
    try:
        oid = ObjectId(category_id)
    except Exception:
        return None
    return get_db()["categories"].find_one({"_id": oid})
