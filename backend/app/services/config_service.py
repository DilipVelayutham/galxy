from bson import ObjectId
from app.db import db

class ConfigService:
    @staticmethod
    def validate_attributes(category_id_str, selected_attributes):
        category = db.categories.find_one({"_id": ObjectId(category_id_str)})
        if not category:
            return False, "Category not found", {}
            
        schema = category.get("attribute_schema", [])
        errors = {}
        validated = {}
        
        # Check attributes
        for item in schema:
            key = item["key"]
            label = item["label"]
            req = item.get("required", False)
            item_type = item["type"]
            
            val = selected_attributes.get(key)
            
            # Check required
            if req and val is None:
                errors[key] = f"{label} is required."
                continue
                
            if val is None:
                continue
                
            # Type specific checks
            if item_type in ["select", "color_swatch", "image_swatch"]:
                # Must be one of the option values
                options = item.get("options", [])
                valid_values = [opt["value"] for opt in options]
                if val not in valid_values:
                    errors[key] = f"Invalid selection for {label}. Selected '{val}', expected one of: {valid_values}"
                else:
                    validated[key] = val
                    
            elif item_type == "toggle":
                if not isinstance(val, bool):
                    errors[key] = f"{label} must be a boolean."
                else:
                    validated[key] = val
                    
            elif item_type in ["number", "slider"]:
                try:
                    num_val = float(val)
                    min_val = item.get("min")
                    max_val = item.get("max")
                    
                    if min_val is not None and num_val < float(min_val):
                        errors[key] = f"{label} cannot be less than {min_val}."
                    elif max_val is not None and num_val > float(max_val):
                        errors[key] = f"{label} cannot be greater than {max_val}."
                    else:
                        validated[key] = num_val
                except (ValueError, TypeError):
                    errors[key] = f"{label} must be a number."
                    
            elif item_type == "text_input":
                if not isinstance(val, str):
                    errors[key] = f"{label} must be text."
                else:
                    validated[key] = val
            else:
                validated[key] = val
                
        if errors:
            return False, "Validation failed", errors
            
        return True, "Validation successful", validated

    @staticmethod
    def calculate_price(product_id_str, selected_attributes):
        product = db.products.find_one({"_id": ObjectId(product_id_str)})
        if not product:
            return None, "Product not found"
            
        base_price = product.get("base_price", 0.0)
        category_id = product.get("category_id")
        
        category = db.categories.find_one({"_id": category_id})
        if not category:
            return None, "Category not found"
            
        schema = category.get("attribute_schema", [])
        total_price = base_price
        breakdown = [{"name": "Base Price", "price": base_price}]
        
        for item in schema:
            key = item["key"]
            item_type = item["type"]
            val = selected_attributes.get(key)
            
            if val is None:
                continue
                
            # If it's a select/swatch, search the matching option price delta
            if item_type in ["select", "color_swatch", "image_swatch"]:
                options = item.get("options", [])
                for opt in options:
                    if opt["value"] == val:
                        delta = float(opt.get("price_delta", 0.0))
                        if delta != 0:
                            total_price += delta
                            breakdown.append({"name": f"{item['label']}: {opt['label']}", "price": delta})
                            
            # Other input types don't default to specific option price deltas in the schema, 
            # but if they had price deltas we could process them here.
            
        return {
            "base_price": base_price,
            "total_price": total_price,
            "breakdown": breakdown
        }, None
