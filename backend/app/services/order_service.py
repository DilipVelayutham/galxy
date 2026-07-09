import datetime
from bson import ObjectId
from app.db import db
from app.services.config_service import ConfigService

class OrderService:
    @staticmethod
    def generate_order_number():
        now = datetime.datetime.utcnow()
        year = now.year
        
        # Start and end of the current year
        start_of_year = datetime.datetime(year, 1, 1)
        end_of_year = datetime.datetime(year + 1, 1, 1)
        
        # Count orders in the current year
        count = db.orders.count_documents({
            "created_at": {
                "$gte": start_of_year,
                "$lt": end_of_year
            }
        })
        
        return f"GLX-{year}-{count + 1:05d}"

    @classmethod
    def checkout(cls, user_id_str, address_id_str):
        # 1. Fetch user & default/specified address
        user = db.users.find_one({"_id": ObjectId(user_id_str)})
        if not user:
            return None, "User not found"
            
        addresses = user.get("addresses", [])
        selected_address = None
        
        if address_id_str:
            for addr in addresses:
                if str(addr.get("id")) == address_id_str:
                    selected_address = addr
                    break
        else:
            # Fallback to default
            for addr in addresses:
                if addr.get("is_default"):
                    selected_address = addr
                    break
            if not selected_address and addresses:
                selected_address = addresses[0]
                
        if not selected_address:
            return None, "Shipping address is required to place an order"
            
        # 2. Fetch cart
        cart = db.carts.find_one({"user_id": ObjectId(user_id_str)})
        if not cart or not cart.get("items"):
            return None, "Shopping cart is empty"
            
        cart_items = cart["items"]
        order_items = []
        estimated_total = 0.0
        
        # 3. Validate & compile items
        for item in cart_items:
            prod_id = item["product_id"]
            product = db.products.find_one({"_id": prod_id, "is_active": True})
            
            if not product:
                return None, f"Product {prod_id} is no longer available"
                
            if product.get("stock_status") == "out_of_stock":
                return None, f"Product '{product.get('title')}' is currently out of stock"
                
            # Fetch category name
            cat = db.categories.find_one({"_id": product["category_id"]})
            category_name = cat["name"] if cat else "Bespoke"
            
            # Re-calculate pricing to double check
            pricing, err = ConfigService.calculate_price(str(prod_id), item["selected_attributes"])
            if err:
                return None, f"Config error on '{product.get('title')}': {err}"
                
            unit_price = pricing["total_price"]
            subtotal = unit_price * item["quantity"]
            estimated_total += subtotal
            
            order_items.append({
                "product_id": prod_id,
                "product_title": product["title"],
                "category_name": category_name,
                "selected_attributes": item["selected_attributes"],
                "quantity": item["quantity"],
                "unit_price_estimate": unit_price,
                "ai_preview_image": item.get("ai_preview_image"),
                "reference_image": item.get("reference_image") # User uploaded if any
            })
            
        # 4. Create Order
        order_number = cls.generate_order_number()
        
        customer_snapshot = {
            "name": user["name"],
            "phone": user.get("phone", ""),
            "email": user["email"],
            "address": {
                "line1": selected_address["line1"],
                "line2": selected_address.get("line2", ""),
                "city": selected_address["city"],
                "state": selected_address["state"],
                "pincode": selected_address["pincode"]
            }
        }
        
        status_entry = {
            "status": "received",
            "note": "Order inquiry received, awaiting review.",
            "updated_by": ObjectId(user_id_str),
            "timestamp": datetime.datetime.utcnow()
        }
        
        new_order = {
            "order_number": order_number,
            "user_id": ObjectId(user_id_str),
            "customer_snapshot": customer_snapshot,
            "items": order_items,
            "estimated_total": estimated_total,
            "final_quoted_price": None,
            "status": "received",
            "status_history": [status_entry],
            "admin_notes": "",
            "customer_visible_note": "Order inquiry received, awaiting review.",
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
        
        # Save order
        db.orders.insert_one(new_order)
        
        # 5. Clear cart
        db.carts.update_one({"user_id": ObjectId(user_id_str)}, {"$set": {"items": [], "updated_at": datetime.datetime.utcnow()}})
        
        return order_number, None

    @classmethod
    def has_delivered_order_for_product(cls, user_id_str, product_id_str):
        # Look for delivered orders containing this product for this user
        delivered_orders = db.orders.find({
            "user_id": ObjectId(user_id_str),
            "status": "delivered",
            "items.product_id": ObjectId(product_id_str)
        })
        
        orders_list = list(delivered_orders)
        if not orders_list:
            return {"eligible": False}
            
        # Return details of the first eligible order
        first_order = orders_list[0]
        return {
            "eligible": True,
            "order_id": str(first_order["_id"]),
            "order_number": first_order["order_number"]
        }
