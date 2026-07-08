# app/models/testimonial.py
import datetime

class TestimonialModel:
    """
    MongoDB Schema Representation:
    Collection: testimonials
    
    Fields:
      _id: ObjectId
      source: string ("review" | "manual")
      review_id: ObjectId | None
      customer_name: string
      customer_location: string (e.g. 'Chennai')
      quote: string
      rating: integer (1-5)
      image: string | None (Cloudinary URL)
      display_order: integer
      is_active: boolean
      created_at: datetime
    """
    @staticmethod
    def get_validator():
        return {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["source", "customer_name", "quote", "rating"],
                "properties": {
                    "source": {"enum": ["review", "manual"]},
                    "review_id": {"bsonType": ["objectId", "null"]},
                    "customer_name": {"bsonType": "string"},
                    "customer_location": {"bsonType": "string"},
                    "quote": {"bsonType": "string"},
                    "rating": {"bsonType": "int", "minimum": 1, "maximum": 5},
                    "image": {"bsonType": ["string", "null"]},
                    "display_order": {"bsonType": "int"},
                    "is_active": {"bsonType": "bool"},
                    "created_at": {"bsonType": "date"}
                }
            }
        }
