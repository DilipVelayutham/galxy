from datetime import datetime, timezone
from bson import ObjectId

class AIGeneration:
    @staticmethod
    def get_collection():
        # Import app locally to avoid circular dependencies
        import app
        return app.db["ai_generations"]

    @staticmethod
    def create_indexes():
        col = AIGeneration.get_collection()
        col.create_index("user_id")
        col.create_index("session_id")
        col.create_index("category_id")
        col.create_index("created_at")

    @staticmethod
    def insert(
        user_id,
        session_id,
        category_id,
        product_id,
        selected_attributes,
        prompt_used,
        input_reference_image,
        output_image_url,
        provider,
        status,
        error_message,
        generation_time_ms
    ):
        record = {
            "user_id": ObjectId(user_id) if user_id else None,
            "session_id": session_id,
            "category_id": ObjectId(category_id) if category_id else None,
            "product_id": ObjectId(product_id) if product_id else None,
            "selected_attributes": selected_attributes,
            "prompt_used": prompt_used,
            "input_reference_image": input_reference_image,
            "output_image_url": output_image_url,
            "provider": provider or "gemini",
            "status": status,  # "success" | "failed" | "rate_limited"
            "error_message": error_message,
            "generation_time_ms": generation_time_ms,
            "created_at": datetime.now(timezone.utc)
        }
        result = AIGeneration.get_collection().insert_one(record)
        record["_id"] = result.inserted_id
        return record
