import logging
import os
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import PyMongoError
from flask import current_app
from app.db import get_db
from app.models.wishlist import Wishlist, get_wishlist_by_user, create_wishlist
from app.models.product import get_product, is_product_active

class DatabaseErrorFetchingProducts(PyMongoError):
    """
    Exception raised when a database error occurs while querying products.
    """
    pass

def _get_logger() -> logging.Logger:
    """
    Get the appropriate logger. Uses Flask's current_app logger when in an app context,
    otherwise falls back to a standard Python logger.
    """
    try:
        return current_app.logger
    except RuntimeError:
        return logging.getLogger("app.services.wishlist_service")

def get_or_create(user_id) -> dict:
    """
    Get the wishlist for the user, or create one if it doesn't exist.
    """
    logger = _get_logger()
    try:
        u_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
    except (InvalidId, TypeError) as e:
        logger.warning({
            "event": "invalid_user_id_format_in_service",
            "user_id": str(user_id),
            "error": str(e)
        })
        raise ValueError(f"Invalid user ID format: {str(e)}") from e

    try:
        db = get_db()
        wishlist_doc = db.wishlists.find_one({"user_id": u_id})
        if not wishlist_doc:
            new_wishlist = Wishlist(user_id=u_id)
            db.wishlists.insert_one(new_wishlist.to_dict())
            wishlist_doc = new_wishlist.to_dict()
            logger.info({
                "event": "wishlist_created",
                "user_id": str(u_id)
            })
        return wishlist_doc
    except PyMongoError as e:
        logger.error({
            "event": "db_error_in_get_or_create",
            "user_id": str(u_id),
            "error": str(e)
        }, exc_info=True)
        raise

def get_or_create_wishlist(user_id) -> dict:
    """
    Alias for get_or_create to maintain compatibility with develop branch.
    """
    return get_or_create(user_id)

def add_to_wishlist(user_id, product_id) -> int:
    """
    Add a product to the wishlist. Validates if the product exists first.
    Returns the updated count of wishlist items.
    """
    logger = _get_logger()
    try:
        u_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
    except (InvalidId, TypeError) as e:
        logger.warning({
            "event": "invalid_user_id_format_in_add",
            "user_id": str(user_id),
            "error": str(e)
        })
        raise ValueError(f"Invalid user ID format: {str(e)}") from e

    try:
        p_id = ObjectId(product_id) if isinstance(product_id, str) else product_id
    except (InvalidId, TypeError) as e:
        logger.warning({
            "event": "invalid_product_id_format_in_add",
            "product_id": str(product_id),
            "error": str(e)
        })
        raise ValueError(f"Invalid product ID format: {str(e)}") from e

    try:
        db = get_db()
        # 1. Validate product exists in Module 3
        product = db.products.find_one({"_id": p_id})
        if not product:
            logger.warning({
                "event": "add_non_existent_product_to_wishlist",
                "user_id": str(u_id),
                "product_id": str(p_id)
            })
            raise ValueError("Product not found")

        # 2. Check if product is active and not soft-deleted
        if not is_product_active(product):
            logger.warning({
                "event": "add_inactive_product_to_wishlist",
                "user_id": str(u_id),
                "product_id": str(p_id)
            })
            raise ValueError("Product is soft-deleted or inactive")

        # Ensure wishlist document exists
        get_or_create(u_id)

        # 3. Add product_id using $addToSet for idempotence
        wishlist_doc = db.wishlists.find_one_and_update(
            {"user_id": u_id},
            {
                "$addToSet": {"product_ids": p_id},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            },
            return_document=True
        )

        count = len(wishlist_doc.get("product_ids", [])) if wishlist_doc else 0
        logger.info({
            "event": "product_added_to_wishlist",
            "user_id": str(u_id),
            "product_id": str(p_id),
            "count": count
        })
        return count
    except PyMongoError as e:
        logger.error({
            "event": "db_error_in_add_to_wishlist",
            "user_id": str(u_id),
            "product_id": str(p_id),
            "error": str(e)
        }, exc_info=True)
        raise

def remove_from_wishlist(user_id, product_id) -> int:
    """
    Remove a product from the wishlist.
    """
    logger = _get_logger()
    try:
        u_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
    except (InvalidId, TypeError) as e:
        logger.warning({
            "event": "invalid_user_id_format_in_remove",
            "user_id": str(user_id),
            "error": str(e)
        })
        raise ValueError(f"Invalid user ID format: {str(e)}") from e

    try:
        p_id = ObjectId(product_id) if isinstance(product_id, str) else product_id
    except (InvalidId, TypeError) as e:
        logger.warning({
            "event": "invalid_product_id_format_in_remove",
            "product_id": str(product_id),
            "error": str(e)
        })
        raise ValueError(f"Invalid product ID format: {str(e)}") from e

    try:
        db = get_db()
        # Pull the product_id from the wishlist array (idempotent pull)
        wishlist_doc = db.wishlists.find_one_and_update(
            {"user_id": u_id},
            {
                "$pull": {"product_ids": p_id},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            },
            return_document=True
        )

        count = len(wishlist_doc.get("product_ids", [])) if wishlist_doc else 0
        logger.info({
            "event": "product_removed_from_wishlist",
            "user_id": str(u_id),
            "product_id": str(p_id),
            "count": count
        })
        return count
    except PyMongoError as e:
        logger.error({
            "event": "db_error_in_remove_from_wishlist",
            "user_id": str(u_id),
            "product_id": str(p_id),
            "error": str(e)
        }, exc_info=True)
        raise

def is_product_wishlisted(user_id, product_id) -> bool:
    """
    Check if a product is in the user's wishlist.
    """
    logger = _get_logger()
    try:
        u_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
    except (InvalidId, TypeError) as e:
        logger.warning({
            "event": "invalid_user_id_format_in_check",
            "user_id": str(user_id),
            "error": str(e)
        })
        raise ValueError(f"Invalid user ID format: {str(e)}") from e

    try:
        p_id = ObjectId(product_id) if isinstance(product_id, str) else product_id
    except (InvalidId, TypeError) as e:
        logger.warning({
            "event": "invalid_product_id_format_in_check",
            "product_id": str(product_id),
            "error": str(e)
        })
        raise ValueError(f"Invalid product ID format: {str(e)}") from e

    try:
        db = get_db()
        wishlist = db.wishlists.find_one({"user_id": u_id, "product_ids": p_id})
        is_wishlisted = wishlist is not None
        logger.debug({
            "event": "wishlist_membership_checked",
            "user_id": str(u_id),
            "product_id": str(p_id),
            "is_wishlisted": is_wishlisted
        })
        return is_wishlisted
    except PyMongoError as e:
        logger.error({
            "event": "db_error_in_is_product_wishlisted",
            "user_id": str(u_id),
            "product_id": str(p_id),
            "error": str(e)
        }, exc_info=True)
        raise

def get_hydrated_wishlist(user_id) -> dict:
    """
    Retrieves the wishlist and hydrates product details.
    Retains soft-deleted products but sets is_available = False.
    Avoids N+1 queries by using batch database lookup with $in.
    Resolves category slug using either product's category_slug or looking up category_id.
    """
    db = get_db()
    u_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
    wishlist = get_or_create(u_id)
    
    product_ids = wishlist.get("product_ids", [])
    hydrated_products = []
    
    if product_ids:
        # Normalize product_ids to ObjectIds where possible for the DB query
        query_product_ids = []
        for pid in product_ids:
            if isinstance(pid, ObjectId):
                query_product_ids.append(pid)
            elif isinstance(pid, str):
                try:
                    query_product_ids.append(ObjectId(pid))
                except (InvalidId, TypeError):
                    query_product_ids.append(pid)
            else:
                query_product_ids.append(pid)

        # Batch query products
        try:
            products_cursor = db.products.find({"_id": {"$in": query_product_ids}})
            products_map = {p["_id"]: p for p in products_cursor}
        except PyMongoError as e:
            _get_logger().error({
                "event": "database_error_fetching_products",
                "product_ids": [str(pid) for pid in product_ids],
                "error": str(e)
            }, exc_info=True)
            raise DatabaseErrorFetchingProducts("Database error retrieving products") from e
        
        # Batch query categories
        category_ids = set()
        for product in products_map.values():
            cat_id = product.get("category_id")
            if cat_id:
                try:
                    category_ids.add(ObjectId(cat_id) if isinstance(cat_id, (str, ObjectId)) else cat_id)
                except (InvalidId, TypeError):
                    pass
                    
        categories_map = {}
        if category_ids:
            try:
                categories_cursor = db.categories.find({"_id": {"$in": list(category_ids)}})
                categories_map = {c["_id"]: c for c in categories_cursor}
            except Exception as e:
                _get_logger().warning({
                    "event": "database_error_fetching_categories",
                    "category_ids": [str(cid) for cid in category_ids],
                    "error": str(e)
                }, exc_info=True)
                
        for pid in product_ids:
            normalized_pid = pid
            if isinstance(pid, str):
                try:
                    normalized_pid = ObjectId(pid)
                except (InvalidId, TypeError):
                    pass
                    
            product = products_map.get(normalized_pid)
            if product:
                active = product.get("active", product.get("is_active", True))
                is_deleted = product.get("is_deleted", False)
                is_available = active and not is_deleted
                
                # Retrieve category slug
                category_slug = product.get("category_slug")
                if not category_slug:
                    category_id = product.get("category_id")
                    if category_id:
                        try:
                            cat_obj_id = ObjectId(category_id) if isinstance(category_id, (str, ObjectId)) else category_id
                            category = categories_map.get(cat_obj_id)
                            if category:
                                category_slug = category.get("slug")
                        except Exception as e:
                            _get_logger().warning({
                                "event": "invalid_category_id_lookup",
                                "product_id": str(pid),
                                "category_id": str(category_id),
                                "error": str(e)
                            })
                
                hydrated_products.append({
                    "_id": str(pid),
                    "title": product.get("title", ""),
                    "slug": product.get("slug", ""),
                    "thumbnail": product.get("thumbnail", ""),
                    "base_price": product.get("base_price", 0.0),
                    "category_slug": category_slug,
                    "stock_status": product.get("stock_status", "out_of_stock"),
                    "is_available": is_available
                })
            else:
                # Handle product not found in database anymore (graceful degradation)
                _get_logger().warning({
                    "event": "product_not_found_in_db",
                    "product_id": str(pid)
                })
                hydrated_products.append({
                    "_id": str(pid),
                    "title": "Unknown Product",
                    "slug": "",
                    "thumbnail": "",
                    "base_price": 0.0,
                    "category_slug": None,
                    "stock_status": "out_of_stock",
                    "is_available": False
                })
                
    return {
        "products": hydrated_products,
        "count": len(hydrated_products)
    }

def get_wishlist_ids(user_id) -> list:
    """
    Retrieves a flat list of product ID strings wishlisted by the user.
    """
    u_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
    wishlist = get_or_create(u_id)
    product_ids = wishlist.get("product_ids", [])
    return [str(p_id) for p_id in product_ids]
