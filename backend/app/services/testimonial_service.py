# app/services/testimonial_service.py
import datetime
from bson import ObjectId
from app.db import db

class TestimonialService:
    @staticmethod
    def get_active_testimonials():
        testimonials = list(db.testimonials.find({"is_active": True}).sort("display_order", 1))
        for t in testimonials:
            t["_id"] = str(t["_id"])
            if t.get("review_id"):
                t["review_id"] = str(t["review_id"])
        return testimonials

    @staticmethod
    def promote_from_review(review_id_str, customer_location="Chennai", display_order=0):
        review = db.reviews.find_one({"_id": ObjectId(review_id_str)})
        if not review:
            return None, "Review not found"
            
        if not review.get("is_approved"):
            return None, "Cannot promote unapproved review"
            
        new_testimonial = {
            "source": "review",
            "review_id": review["_id"],
            "customer_name": review["customer_name"],
            "customer_location": customer_location,
            "quote": review["comment"],
            "rating": review["rating"],
            "image": review["images"][0] if review.get("images") else None,
            "display_order": display_order,
            "is_active": True,
            "created_at": datetime.datetime.utcnow()
        }
        
        res = db.testimonials.insert_one(new_testimonial)
        new_testimonial["_id"] = str(res.inserted_id)
        new_testimonial["review_id"] = str(new_testimonial["review_id"])
        return new_testimonial, None

    @staticmethod
    def create_manual_testimonial(name, quote, location="", rating=5, image=None, display_order=0, is_active=True):
        new_t = {
            "source": "manual",
            "review_id": None,
            "customer_name": name,
            "customer_location": location,
            "quote": quote,
            "rating": int(rating),
            "image": image,
            "display_order": display_order,
            "is_active": is_active,
            "created_at": datetime.datetime.utcnow()
        }
        res = db.testimonials.insert_one(new_t)
        new_t["_id"] = str(res.inserted_id)
        return new_t

    @staticmethod
    def update_testimonial(testimonial_id_str, data):
        update_fields = {}
        for f in ["customer_name", "customer_location", "quote", "rating", "image", "display_order", "is_active"]:
            if f in data:
                update_fields[f] = data[f]
                
        res = db.testimonials.update_one({"_id": ObjectId(testimonial_id_str)}, {"$set": update_fields})
        return res.matched_count > 0

    @staticmethod
    def delete_testimonial(testimonial_id_str):
        res = db.testimonials.delete_one({"_id": ObjectId(testimonial_id_str)})
        return res.deleted_count > 0

    @staticmethod
    def reorder_testimonials(reorder_items):
        for item in reorder_items:
            t_id = item.get("testimonial_id")
            disp = item.get("display_order")
            if t_id and disp is not None:
                db.testimonials.update_one({"_id": ObjectId(t_id)}, {"$set": {"display_order": int(disp)}})
        return True
