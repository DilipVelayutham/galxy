from bson import ObjectId
from app.db import get_db, get_reviews_col

class RatingRollupService:
    @staticmethod
    def recalculate_product_rating(product_id):
        """
        Recalculates rating_avg and rating_count for the given product.
        Only fetches approved reviews. Updates the products collection document.
        """
        def to_bson_id(val):
            if isinstance(val, str) and ObjectId.is_valid(val):
                return ObjectId(val)
            return val

        product_oid = to_bson_id(product_id)
        reviews_col = get_reviews_col()
        
        # Fetch only approved reviews for this product
        approved_reviews = list(reviews_col.find({
            "product_id": product_oid,
            "is_approved": True
        }))
        
        rating_count = len(approved_reviews)
        if rating_count == 0:
            rating_avg = 0.0
        else:
            rating_sum = sum(float(r.get("rating", 0)) for r in approved_reviews)
            rating_avg = round(rating_sum / rating_count, 2)
            
        # Update product document in the "products" collection
        db = get_db()
        db["products"].update_one(
            {"_id": product_oid},
            {"$set": {
                "rating_avg": rating_avg,
                "rating_count": rating_count
            }}
        )
        return rating_avg, rating_count
