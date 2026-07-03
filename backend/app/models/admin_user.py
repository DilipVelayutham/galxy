from datetime import datetime, timezone
from bson import ObjectId

class AdminUser:
    @staticmethod
    def create_document(name, email, password_hash):
        """
        Creates a dictionary representation of an admin user document.
        """
        now = datetime.now(timezone.utc)
        return {
            "name": name,
            "email": email.strip().lower(),
            "password_hash": password_hash,
            "role": "super_admin",
            "is_active": True,
            "created_at": now,
            "last_login": None
        }

    @staticmethod
    def to_public_dict(admin_doc):
        """
        Returns an admin document representation safe for public exposure.
        Ensures password_hash is omitted, and converts ObjectId to string.
        """
        if not admin_doc:
            return None
        doc = dict(admin_doc)
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        doc.pop("password_hash", None)
        return doc
