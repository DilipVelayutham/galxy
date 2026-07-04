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
    if not category_id:
        return None
        
    try:
        # Check if it's a valid 24-character hex string for ObjectId
        if isinstance(category_id, str) and len(category_id) == 24 and all(c in '0123456789abcdefABCDEF' for c in category_id):
            oid = ObjectId(category_id)
        else:
            oid = None
    except Exception:
        oid = None

    query = {"$or": []}
    if oid:
        query["$or"].append({"_id": oid})
    query["$or"].append({"category_id": category_id})
    query["$or"].append({"_id": category_id})  # handle string _id in test DBs

    try:
        return get_db()["categories"].find_one(query)
    except Exception:
        return None

