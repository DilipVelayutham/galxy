# app/services/rating_rollup_service.py
from bson import ObjectId
from app.db import db

class RatingRollupService:
    @staticmethod
    def recalculate_product_rating(product_id_str):
        product_id = ObjectId(product_id_str)
        
        # Calculate rolls only for approved reviews
        approved_reviews = list(db.reviews.find({
            "product_id": product_id,
            "is_approved": True
        }))
        
        ratings = [r["rating"] for r in approved_reviews]
        count = len(ratings)
        avg = round(sum(ratings) / count, 1) if count > 0 else 0.0
        
        # Sole writer updates to Module 3's product rating averages
        db.products.update_one(
            {"_id": product_id},
            {"$set": {"rating_avg": avg, "rating_count": count}}
        )
        
        return avg, count
