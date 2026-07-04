from bson import ObjectId
from datetime import datetime
from flask import g
from app.db import get_db, get_reviews_col
from app.models.review import ReviewModel
from app.services.rating_rollup_service import RatingRollupService

# Import order_service (Module 8)
try:
    from app.services.order_service import order_service
except ImportError:
    order_service = None

# Import image upload helper (Module 10)
upload_image = None
try:
    from app.utils.upload import upload_image
except ImportError:
    try:
        from app.services.upload_service import upload_image
    except ImportError:
        try:
            from app.services.cloudinary_service import upload_image
        except ImportError:
            pass


class ReviewService:
    @staticmethod
    def to_bson_id(val):
        """Safely convert a value to BSON ObjectId if it is valid."""
        if isinstance(val, str) and ObjectId.is_valid(val):
            return ObjectId(val)
        return val

    @staticmethod
    def submit_review(product_id, user_id, order_id, order_number, rating, comment, images=None, customer_name=None):
        """
        Submits a new review for a product.
        Verifies purchase history, duplicate submissions, and stores pending review.
        """
        # Check order_service integration
        if order_service is None:
            return {
                "success": False,
                "message": "Order Service (Module 8) integration error: Service is currently unavailable.",
                "errors": {}
            }, 500

        # Check upload_image integration if there are images
        if images and upload_image is None:
            return {
                "success": False,
                "message": "Image Upload Service (Module 10) integration error: Cloudinary helper is currently unavailable.",
                "errors": {}
            }, 500

        # 1. Verify that user has purchased and received the product (using order_service)
        try:
            has_purchased = order_service.has_delivered_order_for_product(user_id, product_id)
        except Exception as e:
            return {
                "success": False,
                "message": f"Order Service integration call error: {str(e)}",
                "errors": {}
            }, 500

        if not has_purchased:
            return {
                "success": False,
                "message": "Product has not been purchased and delivered.",
                "errors": {}
            }, 403

        # 2. Check for duplicate review for this (user_id, product_id, order_id)
        reviews_col = get_reviews_col()
        product_oid = ReviewService.to_bson_id(product_id)
        duplicate = reviews_col.find_one({
            "user_id": str(user_id),
            "product_id": product_oid,
            "order_id": str(order_id)
        })
        if duplicate:
            return {
                "success": False,
                "message": "Review already exists for this purchase.",
                "errors": {}
            }, 409

        # 3. Snapshot customer_name from user profile (Module 1)
        db = get_db()
        final_customer_name = None
        
        # Try finding the user document in users collection
        if user_id:
            user_doc = db["users"].find_one({"_id": ReviewService.to_bson_id(user_id)})
            if user_doc:
                final_customer_name = user_doc.get("name") or user_doc.get("customer_name")

        # Fallback chain for customer name
        if not final_customer_name:
            final_customer_name = customer_name or getattr(g, "user_name", None) or "Anonymous"

        # 4. Handle review images uploading if they are files
        uploaded_image_urls = []
        if images:
            for img in images:
                if hasattr(img, "filename") and img.filename:
                    # It's a file, upload using Module 10 helper
                    url = upload_image(img)
                    uploaded_image_urls.append(url)
                elif isinstance(img, str):
                    # It's already a URL
                    uploaded_image_urls.append(img)

        # 5. Save the review as pending
        review_doc = ReviewModel.create_schema(
            product_id=product_oid,
            user_id=user_id,
            order_id=order_id,
            order_number=order_number,
            rating=rating,
            comment=comment,
            images=uploaded_image_urls,
            customer_name=final_customer_name,
            is_approved=False
        )
        
        res = reviews_col.insert_one(review_doc)
        
        return {
            "success": True,
            "message": "Review submitted, pending approval",
            "data": {
                "id": str(res.inserted_id)
            }
        }, 201

    @staticmethod
    def get_product_reviews(product_id, page=1, limit=20, sort="newest"):
        """
        Retrieves public approved reviews for a product with sorting and pagination.
        Never exposes user_id or order_id.
        """
        product_oid = ReviewService.to_bson_id(product_id)
        reviews_col = get_reviews_col()
        
        query = {
            "product_id": product_oid,
            "is_approved": True
        }
        
        # Determine sorting fields
        if sort == "highest_rated":
            sort_fields = [("rating", -1), ("created_at", -1)]
        elif sort == "lowest_rated":
            sort_fields = [("rating", 1), ("created_at", -1)]
        else: # Default: newest
            sort_fields = [("created_at", -1)]
            
        page = max(1, int(page))
        limit = max(1, int(limit))
        skip = (page - 1) * limit
        
        # Run query
        cursor = reviews_col.find(query).sort(sort_fields).skip(skip).limit(limit)
        reviews = list(cursor)
        
        total = reviews_col.count_documents(query)
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        
        # Serialize reviews using public = True (removes user_id and order_id)
        serialized_reviews = [ReviewModel.serialize(r, public=True) for r in reviews]
        
        return {
            "success": True,
            "data": serialized_reviews,
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": total_pages
        }, 200

    @staticmethod
    def get_admin_reviews(is_approved=None, product_id=None, page=1, limit=20):
        """
        Retrieves all reviews for admin moderation with filtering and pagination.
        """
        reviews_col = get_reviews_col()
        
        query = {}
        
        # Handle approval filter
        if is_approved is not None:
            if isinstance(is_approved, str):
                is_approved_bool = is_approved.lower() == "true"
            else:
                is_approved_bool = bool(is_approved)
            query["is_approved"] = is_approved_bool
            
        # Handle product filter
        if product_id:
            query["product_id"] = ReviewService.to_bson_id(product_id)
            
        page = max(1, int(page))
        limit = max(1, int(limit))
        skip = (page - 1) * limit
        
        # Run query (newest reviews first for moderation convenience)
        cursor = reviews_col.find(query).sort([("created_at", -1)]).skip(skip).limit(limit)
        reviews = list(cursor)
        
        total = reviews_col.count_documents(query)
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        
        # Serialize reviews using public = False (exposes moderation details)
        serialized_reviews = [ReviewModel.serialize(r, public=False) for r in reviews]
        
        return {
            "success": True,
            "data": serialized_reviews,
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": total_pages
        }, 200

    @staticmethod
    def approve_review(review_id):
        """ Approves a pending review and updates the product rollup rating. """
        reviews_col = get_reviews_col()
        review_oid = ReviewService.to_bson_id(review_id)
        
        review = reviews_col.find_one({"_id": review_oid})
        if not review:
            return {
                "success": False,
                "message": "Review not found.",
                "errors": {}
            }, 404
            
        # Set approved
        reviews_col.update_one(
            {"_id": review_oid},
            {
                "$set": {
                    "is_approved": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Recalculate rollup
        RatingRollupService.recalculate_product_rating(review["product_id"])
        
        return {
            "success": True,
            "message": "Review approved successfully",
            "data": {}
        }, 200

    @staticmethod
    def reject_review(review_id, reason=None):
        """ Rejects a review (keeps is_approved=False) and updates rollup if previously approved. """
        reviews_col = get_reviews_col()
        review_oid = ReviewService.to_bson_id(review_id)
        
        review = reviews_col.find_one({"_id": review_oid})
        if not review:
            return {
                "success": False,
                "message": "Review not found.",
                "errors": {}
            }, 404
            
        was_approved = review.get("is_approved", False)
        
        # Update review document
        update_data = {
            "is_approved": False,
            "updated_at": datetime.utcnow()
        }
        if reason is not None:
            update_data["rejection_reason"] = str(reason).strip()
            
        reviews_col.update_one(
            {"_id": review_oid},
            {"$set": update_data}
        )
        
        # Recalculate rollup if it was previously approved and now rejected
        if was_approved:
            RatingRollupService.recalculate_product_rating(review["product_id"])
            
        return {
            "success": True,
            "message": "Review rejected successfully",
            "data": {}
        }, 200

    @staticmethod
    def delete_review(review_id):
        """ Hard-deletes a review from the database. Rollups updated if review was approved. """
        reviews_col = get_reviews_col()
        review_oid = ReviewService.to_bson_id(review_id)
        
        review = reviews_col.find_one({"_id": review_oid})
        if not review:
            return {
                "success": False,
                "message": "Review not found.",
                "errors": {}
            }, 404
            
        was_approved = review.get("is_approved", False)
        
        # Hard delete
        reviews_col.delete_one({"_id": review_oid})
        
        # Recalculate rollup if deleted review was approved
        if was_approved:
            RatingRollupService.recalculate_product_rating(review["product_id"])
            
        return {
            "success": True,
            "message": "Review deleted successfully",
            "data": {}
        }, 200

    @staticmethod
    def promote_to_testimonial(review_id):
        """ Copies the review document fields to the testimonials collection. """
        reviews_col = get_reviews_col()
        review_oid = ReviewService.to_bson_id(review_id)
        
        review = reviews_col.find_one({"_id": review_oid})
        if not review:
            return {
                "success": False,
                "message": "Review not found.",
                "errors": {}
            }, 404
            
        db = get_db()
        
        # Testimonial frozen structure
        testimonial_data = {
            "review_id": review["_id"],
            "product_id": review.get("product_id"),
            "user_id": review.get("user_id"),
            "customer_name": review.get("customer_name"),
            "rating": review.get("rating"),
            "comment": review.get("comment"),
            "images": review.get("images", []),
            "is_featured": review.get("is_featured", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        res = db["testimonials"].insert_one(testimonial_data)
        
        return {
            "success": True,
            "message": "Review successfully promoted to testimonial",
            "data": {
                "testimonial_id": str(res.inserted_id)
            }
        }, 200
