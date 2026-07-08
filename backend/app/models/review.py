# app/models/review.py
import datetime

class ReviewModel:
    """
    MongoDB Schema Representation:
    Collection: reviews
    
    Fields:
      _id: ObjectId
      product_id: ObjectId
      user_id: ObjectId
      order_id: ObjectId
      order_number: string
      rating: integer (1-5)
      comment: string
      images: list of strings (Cloudinary URLs)
      customer_name: string (snapshot)
      is_approved: boolean (default False)
      is_featured: boolean (default False)
      created_at: datetime
      updated_at: datetime
    """
    @staticmethod
    def get_validator():
        return {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["product_id", "user_id", "order_id", "rating", "comment", "customer_name"],
                "properties": {
                    "product_id": {"bsonType": "objectId"},
                    "user_id": {"bsonType": "objectId"},
                    "order_id": {"bsonType": "objectId"},
                    "order_number": {"bsonType": "string"},
                    "rating": {"bsonType": "int", "minimum": 1, "maximum": 5},
                    "comment": {"bsonType": "string"},
                    "images": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    },
                    "customer_name": {"bsonType": "string"},
                    "is_approved": {"bsonType": "bool"},
                    "is_featured": {"bsonType": "bool"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
        }
