from bson import ObjectId
from app.db import get_db

def build_snapshot(product_id):
    """
    Builds the denormalized product/category snapshot fields:
    product_title, category_name, thumbnail, and category_id.
    """
    db = get_db()
    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise ValueError("Product not found")

    category = db.categories.find_one({"_id": ObjectId(product.get("category_id"))})
    category_name = category.get("name") if category else "Unknown Category"

    return {
        "product_title": product.get("title", ""),
        "category_name": category_name,
        "thumbnail": product.get("thumbnail", ""),
        "category_id": product.get("category_id")
    }
