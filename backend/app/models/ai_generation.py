"""
ai_generation.py — Module 5 AI Preview Generation
MongoDB document model for the ai_generations collection.
Owns the schema definition, index declaration, and CRUD helpers.
"""
from datetime import datetime, timezone
from bson import ObjectId
from app.db import get_db


# ─── Collection accessor ─────────────────────────────────────────────────────────
def get_collection():
    """Return the ai_generations collection from the shared DB connection."""
    return get_db()["ai_generations"]


# ─── Index initializer (call once at app startup) ────────────────────────────────
def ensure_indexes():
    """
    Create indexes declared in the Module 5 spec:
      • user_id    — fetching a user's generation history
      • session_id — guest rate limiting
      • category_id — admin usage analytics per category
      • created_at — cleanup/expiry jobs and recent-activity queries
    """
    col = get_collection()
    col.create_index("user_id")
    col.create_index("session_id")
    col.create_index("category_id")
    col.create_index("created_at")


# ─── Document factory ────────────────────────────────────────────────────────────
def build_document(
    *,
    user_id,            # ObjectId | None (None = guest)
    session_id: str,    # always present; guest tracking / rate-limit key
    category_id,        # ObjectId
    product_id,         # ObjectId | None
    selected_attributes: dict,
    prompt_used: str,
    input_reference_image: str | None,
    output_image_url: str,
    provider: str,
    status: str,        # "success" | "failed" | "rate_limited"
    error_message: str | None = None,
    generation_time_ms: int = 0,
) -> dict:
    """
    Construct a raw dict ready to be inserted into ai_generations.
    No DB calls here — caller is responsible for the insert.
    """
    return {
        "_id": ObjectId(),
        "user_id": user_id,
        "session_id": session_id,
        "category_id": category_id,
        "product_id": product_id,
        "selected_attributes": selected_attributes,
        "prompt_used": prompt_used,
        "input_reference_image": input_reference_image,
        "output_image_url": output_image_url,
        "provider": provider,
        "status": status,
        "error_message": error_message,
        "generation_time_ms": generation_time_ms,
        "created_at": datetime.now(timezone.utc),
    }


# ─── Insert ──────────────────────────────────────────────────────────────────────
def insert_generation(doc: dict) -> str:
    """Insert a generation document; return its string _id."""
    result = get_collection().insert_one(doc)
    return str(result.inserted_id)


# ─── Queries ─────────────────────────────────────────────────────────────────────
def get_user_generations(user_id, page: int = 1, per_page: int = 20) -> list[dict]:
    """
    Return paginated generation history for a logged-in user,
    most-recent first. Serializes ObjectIds to strings.
    """
    col = get_collection()
    skip = (page - 1) * per_page
    cursor = (
        col.find(
            {"user_id": ObjectId(user_id), "status": "success"},
            {
                "_id": 1,
                "category_id": 1,
                "product_id": 1,
                "selected_attributes": 1,
                "output_image_url": 1,
                "created_at": 1,
            },
        )
        .sort("created_at", -1)
        .skip(skip)
        .limit(per_page)
    )
    return [_serialize(doc) for doc in cursor]


def count_user_generations(user_id) -> int:
    """Total successful generations for a user (for pagination)."""
    return get_collection().count_documents(
        {"user_id": ObjectId(user_id), "status": "success"}
    )


def get_all_generations_admin(
    *,
    category_id=None,
    status: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    per_page: int = 50,
) -> tuple[list[dict], int]:
    """
    Admin query: full list with optional filters. Returns (docs, total_count).
    """
    col = get_collection()
    query: dict = {}
    if category_id:
        query["category_id"] = ObjectId(category_id)
    if status:
        query["status"] = status
    if date_from or date_to:
        query["created_at"] = {}
        if date_from:
            query["created_at"]["$gte"] = date_from
        if date_to:
            query["created_at"]["$lte"] = date_to

    total = col.count_documents(query)
    skip = (page - 1) * per_page
    cursor = col.find(query).sort("created_at", -1).skip(skip).limit(per_page)
    return [_serialize(doc) for doc in cursor], total


# ─── Helpers ─────────────────────────────────────────────────────────────────────
def _serialize(doc: dict) -> dict:
    """Convert ObjectId fields to strings for JSON serialization."""
    for key in ("_id", "user_id", "category_id", "product_id"):
        if key in doc and isinstance(doc[key], ObjectId):
            doc[key] = str(doc[key])
    return doc
