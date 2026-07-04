import datetime
from datetime import timezone
from bson import ObjectId
from app.db import get_db

# ─── Class-based Model (HEAD) ───────────────────────────────────────────────────

class AIGeneration:
    """
    Represents the database model for the m5_generations collection.
    Adheres strictly to the document schema.
    """
    def __init__(self, category_id, selected_attributes, output_image_url, 
                 user_id=None, session_id=None, ip_address=None, product_id=None, prompt_used="", 
                 input_reference_image=None, provider="gemini", status="success", 
                 error_message=None, generation_time_ms=0, created_at=None):
        self.user_id = user_id
        self.session_id = session_id
        self.ip_address = ip_address
        self.category_id = category_id
        self.product_id = product_id
        self.selected_attributes = selected_attributes
        self.prompt_used = prompt_used
        self.input_reference_image = input_reference_image
        self.output_image_url = output_image_url
        self.provider = provider
        self.status = status
        self.error_message = error_message
        self.generation_time_ms = generation_time_ms
        self.created_at = created_at or datetime.datetime.now(timezone.utc)

    def to_dict(self):
        """Converts the model fields into a dictionary matching MongoDB storage format."""
        user_obj_id = None
        if self.user_id:
            try:
                user_obj_id = ObjectId(self.user_id) if isinstance(self.user_id, str) else self.user_id
            except Exception:
                user_obj_id = self.user_id

        cat_obj_id = None
        if self.category_id:
            try:
                cat_obj_id = ObjectId(self.category_id) if isinstance(self.category_id, str) else self.category_id
            except Exception:
                cat_obj_id = self.category_id

        prod_obj_id = None
        if self.product_id:
            try:
                prod_obj_id = ObjectId(self.product_id) if isinstance(self.product_id, str) else self.product_id
            except Exception:
                prod_obj_id = self.product_id

        return {
            "user_id": user_obj_id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "category_id": cat_obj_id,
            "product_id": prod_obj_id,
            "selected_attributes": self.selected_attributes,
            "prompt_used": self.prompt_used,
            "input_reference_image": self.input_reference_image,
            "output_image_url": self.output_image_url,
            "provider": self.provider,
            "status": self.status,
            "error_message": self.error_message,
            "generation_time_ms": self.generation_time_ms,
            "created_at": self.created_at
        }
        
    @staticmethod
    def from_dict(doc):
        """Creates an AIGeneration model instance from a MongoDB document dict."""
        if not doc:
            return None
        return AIGeneration(
            user_id=doc.get("user_id"),
            session_id=doc.get("session_id"),
            ip_address=doc.get("ip_address"),
            category_id=doc.get("category_id"),
            product_id=doc.get("product_id"),
            selected_attributes=doc.get("selected_attributes"),
            prompt_used=doc.get("prompt_used"),
            input_reference_image=doc.get("input_reference_image"),
            output_image_url=doc.get("output_image_url"),
            provider=doc.get("provider", "gemini"),
            status=doc.get("status"),
            error_message=doc.get("error_message"),
            generation_time_ms=doc.get("generation_time_ms", 0),
            created_at=doc.get("created_at")
        )

# ─── Function-based Query & Indexing Utilities (origin/main) ─────────────────────

def get_collection():
    """Return the ai_generations collection from the shared DB connection."""
    return get_db()["ai_generations"]


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
        "created_at": datetime.datetime.now(timezone.utc) if hasattr(datetime, 'datetime') else datetime.now(timezone.utc),
    }


def insert_generation(doc: dict) -> str:
    """Insert a generation document; return its string _id."""
    result = get_collection().insert_one(doc)
    return str(result.inserted_id)


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
    date_from: datetime.datetime | None = None,
    date_to: datetime.datetime | None = None,
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


def _serialize(doc: dict) -> dict:
    """Convert ObjectId fields to strings for JSON serialization."""
    for key in ("_id", "user_id", "category_id", "product_id"):
        if key in doc and isinstance(doc[key], ObjectId):
            doc[key] = str(doc[key])
    return doc

