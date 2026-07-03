from datetime import datetime, timezone
from bson import ObjectId

class User:
    @staticmethod
    def create_document(name, email, phone, password_hash, auth_provider="email"):
        """
        Creates a dictionary representation of a user document.
        """
        now = datetime.now(timezone.utc)
        return {
            "name": name,
            "email": email.strip().lower(),
            "phone": phone.strip() if phone else "",
            "password_hash": password_hash,
            "addresses": [],
            "auth_provider": auth_provider,
            "is_verified": False,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "last_login": None
        }

    @staticmethod
    def to_public_dict(user_doc):
        """
        Returns a user document representation safe for public exposure.
        Ensures password_hash is omitted, and converts ObjectId to string.
        """
        if not user_doc:
            return None
        doc = dict(user_doc)
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        doc.pop("password_hash", None)
        return doc
