import datetime
from bson import ObjectId

class AIGeneration:
    """
    Represents the database model for the m5_generations collection.
    Adheres strictly to the document schema.
    """
    def __init__(self, category_id, selected_attributes, output_image_url, 
                 user_id=None, session_id=None, product_id=None, prompt_used="", 
                 input_reference_image=None, provider="gemini", status="success", 
                 error_message=None, generation_time_ms=0, created_at=None):
        self.user_id = user_id
        self.session_id = session_id
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
        self.created_at = created_at or datetime.datetime.utcnow()

    def to_dict(self):
        """Converts the model fields into a dictionary matching MongoDB storage format."""
        # Convert user_id, category_id, and product_id to ObjectId if they are strings
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
