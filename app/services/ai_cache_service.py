from bson import ObjectId

def check_cache(category_id, selected_attributes):
    # Caching Strategy: Only bypass cache when custom_text (or free text) is present
    if "custom_text" in selected_attributes and selected_attributes["custom_text"]:
        return {"hit": False, "output_image_url": None}
        
    try:
        from app.models.ai_generation import AIGeneration
        col = AIGeneration.get_collection()
        
        # Sort selected_attributes alphabetically to ensure deterministic matching in MongoDB
        sorted_attributes = {k: selected_attributes[k] for k in sorted(selected_attributes.keys())}
        
        # Match identical category and attributes from past successful generations
        match = col.find_one({
            "category_id": ObjectId(category_id) if isinstance(category_id, str) else category_id,
            "selected_attributes": sorted_attributes,
            "status": "success"
        })
        if match:
            return {"hit": True, "output_image_url": match.get("output_image_url")}
    except Exception:
        # Avoid crashing the pipeline if the database is not ready
        pass
        
    return {"hit": False, "output_image_url": None}

def store_cache(category_id, selected_attributes, output_image_url):
    # Logging successful generations acts as storage; stub is kept for contract completeness
    pass
