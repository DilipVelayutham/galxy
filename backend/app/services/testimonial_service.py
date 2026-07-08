import logging
from bson import ObjectId
from pymongo import UpdateOne
from app.database.db import db
from app.models.testimonial import validate_testimonial
from app.utils.database_helper import serialize_doc, serialize_docs

logger = logging.getLogger(__name__)

def get_public_testimonials():
    """
    Returns only is_active: True testimonials, sorted by display_order ascending,
    selecting only public display fields (customer_name, customer_location, quote, rating, image).
    """
    collection = db.get_collection("testimonials")
    if collection is None:
        logger.error("testimonials collection not found")
        return []
    
    projection = {
        "_id": 0,
        "customer_name": 1,
        "customer_location": 1,
        "quote": 1,
        "rating": 1,
        "image": 1
    }
    
    docs = list(collection.find({"is_active": True}, projection).sort("display_order", 1))
    return docs

def get_all_testimonials_admin():
    """
    Returns all testimonials in the database sorted by display_order ascending, for admin display.
    """
    collection = db.get_collection("testimonials")
    if collection is None:
        logger.error("testimonials collection not found")
        return []
    
    docs = list(collection.find().sort("display_order", 1))
    return serialize_docs(docs)

def get_testimonial_by_id(testimonial_id):
    """
    Fetches a single testimonial by its ID.
    """
    collection = db.get_collection("testimonials")
    if collection is None:
        return None
    
    try:
        doc = collection.find_one({"_id": ObjectId(str(testimonial_id))})
        return serialize_doc(doc)
    except Exception as e:
        logger.error(f"Error fetching testimonial {testimonial_id}: {e}")
        return None

def create_testimonial(data):
    """
    Validates and inserts a manual/admin testimonial.
    """
    collection = db.get_collection("testimonials")
    if collection is None:
        raise RuntimeError("Database connection not initialized")
    
    cleaned_data = validate_testimonial(data, is_update=False)
    
    result = collection.insert_one(cleaned_data)
    cleaned_data["_id"] = result.inserted_id
    
    return serialize_doc(cleaned_data)

def update_testimonial(testimonial_id, data):
    """
    Validates and updates an existing testimonial.
    """
    collection = db.get_collection("testimonials")
    if collection is None:
        raise RuntimeError("Database connection not initialized")
        
    try:
        oid = ObjectId(str(testimonial_id))
    except Exception:
        raise ValueError("Invalid testimonial ID format")
        
    cleaned_data = validate_testimonial(data, is_update=True)
    if not cleaned_data:
        raise ValueError("No valid fields to update")
        
    result = collection.update_one({"_id": oid}, {"$set": cleaned_data})
    
    if result.matched_count == 0:
        raise ValueError("Testimonial not found")
        
    updated_doc = collection.find_one({"_id": oid})
    return serialize_doc(updated_doc)

def delete_testimonial(testimonial_id):
    """
    Performs a hard delete on a testimonial.
    """
    collection = db.get_collection("testimonials")
    if collection is None:
        raise RuntimeError("Database connection not initialized")
        
    try:
        oid = ObjectId(str(testimonial_id))
    except Exception:
        raise ValueError("Invalid testimonial ID format")
        
    result = collection.delete_one({"_id": oid})
    return result.deleted_count > 0

def reorder_testimonials(order_list):
    """
    Bulk updates display_order field.
    order_list shape: [{'testimonial_id': str, 'display_order': int}]
    """
    collection = db.get_collection("testimonials")
    if collection is None:
        raise RuntimeError("Database connection not initialized")
        
    if not isinstance(order_list, list):
        raise ValueError("order must be a list")
        
    operations = []
    for item in order_list:
        tid = item.get("testimonial_id") or item.get("id")
        order_val = item.get("display_order")
        
        if not tid or order_val is None:
            raise ValueError("Each order item must contain testimonial_id and display_order")
            
        try:
            oid = ObjectId(str(tid))
            display_order = int(order_val)
        except Exception:
            raise ValueError(f"Invalid testimonial_id or display_order format in item: {item}")
            
        operations.append(
            UpdateOne({"_id": oid}, {"$set": {"display_order": display_order}})
        )
        
    if operations:
        collection.bulk_write(operations)
        
    return True

def promote_review_to_testimonial(review_id, review_data, customer_location=None, display_order=1):
    """
    Function exposed for Module 9A Reviews sub-module.
    Copies an approved review's content into a new testimonial document.
    """
    # Map review properties to testimonial properties
    # A review contains: customer_name, comment, rating, images
    comment = review_data.get("comment") or review_data.get("quote") or ""
    rating = review_data.get("rating", 5)
    customer_name = review_data.get("customer_name") or "Verified Customer"
    images = review_data.get("images") or []
    image = images[0] if (isinstance(images, list) and len(images) > 0) else None
    
    testimonial_payload = {
        "source": "review",
        "review_id": review_id,
        "customer_name": customer_name,
        "customer_location": customer_location or "",
        "quote": comment,
        "rating": rating,
        "image": image,
        "display_order": display_order,
        "is_active": True
    }
    
    return create_testimonial(testimonial_payload)
