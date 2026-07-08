# app/services/review_service.py
import datetime
from bson import ObjectId
from app.db import db
from app.services.order_service import OrderService
from app.services.rating_rollup_service import RatingRollupService

class ReviewService:
    @staticmethod
    def get_product_reviews(product_id_str, sort_by="newest", page=1, limit=20):
        product_id = ObjectId(product_id_str)
        query = {"product_id": product_id, "is_approved": True}
        
        sort_query = [("created_at", -1)]
        if sort_by == "highest_rated":
            sort_query = [("rating", -1), ("created_at", -1)]
        elif sort_by == "lowest_rated":
            sort_query = [("rating", 1), ("created_at", -1)]
            
        total = db.reviews.count_documents(query)
        reviews = list(
            db.reviews.find(query)
            .sort(sort_query)
            .skip((page - 1) * limit)
            .limit(limit)
        )
        
        # Format response mapping (no user_id or order_id)
        formatted = []
        for rev in reviews:
            formatted.append({
                "_id": str(rev["_id"]),
                "customer_name": rev.get("customer_name", "Anonymous"),
                "rating": rev["rating"],
                "comment": rev.get("comment", ""),
                "images": rev.get("images", []),
                "created_at": rev["created_at"].isoformat()
            })
            
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        return formatted, total, total_pages

    @staticmethod
    def create_review(user_id_str, product_id_str, rating, comment, images=None):
        if images is None:
            images = []
            
        # 1. Gate: Verify delivered purchase via Order Service
        eligibility = OrderService.has_delivered_order_for_product(user_id_str, product_id_str)
        if not eligibility.get("eligible"):
            return None, "not a verified delivered purchase", 403
            
        order_id = ObjectId(eligibility["order_id"])
        order_number = eligibility["order_number"]
        
        # 2. Gate: Uniqueness check
        existing = db.reviews.find_one({
            "user_id": ObjectId(user_id_str),
            "product_id": ObjectId(product_id_str),
            "order_id": order_id
        })
        if existing:
            return None, "You've already reviewed this order's purchase of this product", 409
            
        # Fetch user snapshot name
        user = db.users.find_one({"_id": ObjectId(user_id_str)})
        customer_name = user["name"] if user else "Verified Buyer"
        
        new_review = {
            "product_id": ObjectId(product_id_str),
            "user_id": ObjectId(user_id_str),
            "order_id": order_id,
            "order_number": order_number,
            "rating": int(rating),
            "comment": comment,
            "images": images,
            "customer_name": customer_name,
            "is_approved": False,
            "is_featured": False,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
        
        res = db.reviews.insert_one(new_review)
        new_review["_id"] = str(res.inserted_id)
        new_review["product_id"] = str(new_review["product_id"])
        new_review["user_id"] = str(new_review["user_id"])
        new_review["order_id"] = str(new_review["order_id"])
        new_review["created_at"] = new_review["created_at"].isoformat()
        new_review["updated_at"] = new_review["updated_at"].isoformat()
        
        return new_review, "Review submitted, pending approval", 201

    @staticmethod
    def get_admin_reviews(is_approved_bool=None, product_id_str=None, page=1, limit=20):
        query = {}
        if is_approved_bool is not None:
            query["is_approved"] = is_approved_bool
        if product_id_str:
            query["product_id"] = ObjectId(product_id_str)
            
        total = db.reviews.count_documents(query)
        reviews = list(
            db.reviews.find(query)
            .sort("created_at", -1)
            .skip((page - 1) * limit)
            .limit(limit)
        )
        
        for rev in reviews:
            rev["_id"] = str(rev["_id"])
            rev["product_id"] = str(rev["product_id"])
            rev["user_id"] = str(rev["user_id"])
            rev["order_id"] = str(rev["order_id"])
            rev["created_at"] = rev["created_at"].isoformat()
            
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        return reviews, total, total_pages

    @staticmethod
    def approve_review(review_id_str):
        review = db.reviews.find_one({"_id": ObjectId(review_id_str)})
        if not review:
            return None, "Review not found"
            
        db.reviews.update_one(
            {"_id": ObjectId(review_id_str)},
            {"$set": {"is_approved": True, "updated_at": datetime.datetime.utcnow()}}
        )
        
        # Trigger rating rollup
        RatingRollupService.recalculate_product_rating(str(review["product_id"]))
        
        updated = db.reviews.find_one({"_id": ObjectId(review_id_str)})
        updated["_id"] = str(updated["_id"])
        updated["product_id"] = str(updated["product_id"])
        updated["user_id"] = str(updated["user_id"])
        updated["order_id"] = str(updated["order_id"])
        
        return updated, None

    @staticmethod
    def reject_review(review_id_str, reason=""):
        review = db.reviews.find_one({"_id": ObjectId(review_id_str)})
        if not review:
            return False, "Review not found"
            
        db.reviews.update_one(
            {"_id": ObjectId(review_id_str)},
            {"$set": {"is_approved": False, "rejected_reason": reason, "updated_at": datetime.datetime.utcnow()}}
        )
        
        # Recalculate rating rollup in case it was previously approved and is now rejected
        RatingRollupService.recalculate_product_rating(str(review["product_id"]))
        return True, None

    @staticmethod
    def delete_review(review_id_str):
        review = db.reviews.find_one({"_id": ObjectId(review_id_str)})
        if not review:
            return False, "Review not found"
            
        db.reviews.delete_one({"_id": ObjectId(review_id_str)})
        
        # Trigger rating rollup if review was approved
        if review.get("is_approved"):
            RatingRollupService.recalculate_product_rating(str(review["product_id"]))
        return True, None
