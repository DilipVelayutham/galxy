from db import db
from models.cart import to_object_id

def get_product_snapshot(product_id):
    """
    Retrieves product and category details to build a static snapshot 
    of the product at the time it was added to the cart.
    """
    prod_id = to_object_id(product_id)
    product = db.products.find_one({"_id": prod_id})
    if not product:
        raise ValueError(f"Product with ID {product_id} not found in catalog.")
        
    category_name = "General"
    category_id = product.get("category_id")
    if category_id:
        category = db.categories.find_one({"_id": to_object_id(category_id)})
        if category:
            category_name = category.get("name", "General")
            
    return {
        "name": product.get("title", ""),
        "category": category_name,
        "thumbnail": product.get("thumbnail", ""),
        "description": product.get("description", "")
    }
