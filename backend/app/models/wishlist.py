from bson import ObjectId
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.db import get_db

class Wishlist:
    def __init__(self, user_id: Any, product_ids: Optional[List[Any]] = None, updated_at: Optional[datetime] = None, _id: Optional[ObjectId] = None) -> None:
        """
        Initializes a Wishlist object.
        """
        self._id: ObjectId = _id or ObjectId()
        self.user_id: ObjectId = ObjectId(user_id) if isinstance(user_id, (str, ObjectId)) else user_id
        self.product_ids: List[ObjectId] = [ObjectId(pid) if isinstance(pid, (str, ObjectId)) else pid for pid in (product_ids or [])]
        # Use datetime.now(timezone.utc) for timezone-aware or datetime.utcnow() for backward compatibility
        self.updated_at: datetime = updated_at or datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the Wishlist object to a dictionary.
        """
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "product_ids": self.product_ids,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional['Wishlist']:
        """
        Deserializes a Wishlist object from a dictionary.
        """
        if not data:
            return None
        return cls(
            user_id=data.get("user_id"),
            product_ids=data.get("product_ids", []),
            updated_at=data.get("updated_at"),
            _id=data.get("_id")
        )

def ensure_indexes():
    """
    Ensures that the unique index on user_id is created in the wishlists collection.
    """
    db = get_db()
    db.wishlists.create_index("user_id", unique=True)

def get_wishlist_by_user(user_id):
    """
    Fetches the wishlist document associated with a given user_id.
    """
    db = get_db()
    u_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
    return db.wishlists.find_one({"user_id": u_id})

def create_wishlist(user_id):
    """
    Creates an empty wishlist document for a user.
    """
    db = get_db()
    u_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
    wishlist = Wishlist(user_id=u_id)
    db.wishlists.insert_one(wishlist.to_dict())
    return wishlist.to_dict()
