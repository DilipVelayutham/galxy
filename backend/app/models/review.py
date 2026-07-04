from datetime import datetime
from bson import ObjectId

class ReviewModel:
    @staticmethod
    def create_schema(product_id, user_id, order_id, order_number, rating, comment, images=None, customer_name=None, is_approved=False, is_featured=False):
        """Generates a structured dictionary representing the Review schema in MongoDB."""
        def to_bson_id(val):
            if isinstance(val, str) and ObjectId.is_valid(val):
                return ObjectId(val)
            return val
            
        return {
            "product_id": to_bson_id(product_id),
            "user_id": str(user_id) if user_id else None,
            "order_id": str(order_id) if order_id else None,
            "order_number": str(order_number) if order_number else None,
            "rating": int(rating),
            "comment": str(comment).strip() if comment else "",
            "images": list(images) if images else [],
            "customer_name": str(customer_name).strip() if customer_name else "Anonymous",
            "is_approved": bool(is_approved),
            "is_featured": bool(is_featured),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    @staticmethod
    def serialize(review, public=False):
        """
        Serializes a MongoDB Review document to a JSON-compatible dictionary.
        If public is True, user_id and order_id are omitted for privacy.
        """
        if not review:
            return None
            
        serialized = {
            "_id": str(review["_id"]),
            "id": str(review["_id"]),
            "product_id": str(review.get("product_id")),
            "order_number": review.get("order_number"),
            "rating": review.get("rating"),
            "comment": review.get("comment"),
            "images": review.get("images", []),
            "customer_name": review.get("customer_name"),
            "is_approved": review.get("is_approved", False),
            "is_featured": review.get("is_featured", False),
            "created_at": review.get("created_at").isoformat() if isinstance(review.get("created_at"), datetime) else review.get("created_at"),
            "updated_at": review.get("updated_at").isoformat() if isinstance(review.get("updated_at"), datetime) else review.get("updated_at")
        }
        
        # Include rejection reason if present and not a public serialization
        if "rejection_reason" in review:
            serialized["rejection_reason"] = review.get("rejection_reason")
            
        if not public:
            serialized["user_id"] = str(review.get("user_id")) if review.get("user_id") else None
            serialized["order_id"] = str(review.get("order_id")) if review.get("order_id") else None
            
        return serialized
