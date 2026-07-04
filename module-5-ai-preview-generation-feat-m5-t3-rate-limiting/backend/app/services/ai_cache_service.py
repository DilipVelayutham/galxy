import hashlib
import json
import datetime
from bson import ObjectId
from app.database import categories, ai_cache

def _resolve_category(category_or_id):
    """Helper to ensure we have a category document, fetching if necessary."""
    if isinstance(category_or_id, dict):
        return category_or_id
    try:
        try:
            cat_obj_id = ObjectId(category_or_id) if isinstance(category_or_id, str) and len(category_or_id) == 24 else category_or_id
        except Exception:
            cat_obj_id = category_or_id
            
        return categories.find_one({"$or": [{"_id": cat_obj_id}, {"category_id": category_or_id}]})
    except Exception as e:
        print(f"[Cache Service] Error fetching category in cache check: {e}")
        return None

def generate_cache_key(category_or_id, selected_attributes):
    """
    Generates a deterministic SHA256 hash key for caching.
    Sorts attributes alphabetically by key to prevent key-order misses.
    Computes SHA256(category_id + JSON(sorted_cleaned_attributes))
    Uses an unambiguous JSON structure to prevent collisions.
    """
    category = _resolve_category(category_or_id)
    if category:
        cat_str = str(category.get("category_id") or category.get("_id"))
    else:
        cat_str = str(category_or_id)
    
    # Clean selected_attributes to remove None or empty values
    cleaned_attributes = {}
    for k in sorted(selected_attributes.keys()):
        val = selected_attributes[k]
        if val is not None and str(val).strip() != "":
            cleaned_attributes[k] = val
            
    # Serialize to deterministic JSON string
    attrs_json = json.dumps(cleaned_attributes, sort_keys=True)
    combined_string = f"{cat_str}:{attrs_json}"
    sha256 = hashlib.sha256(combined_string.encode('utf-8'))
    return sha256.hexdigest()

def is_cache_bypassed(category_or_id, selected_attributes):
    """
    Returns True if the payload contains custom_text or free text selections,
    which bypasses the cache lookup and storage entirely.
    """
    text_keys = {"custom_text"} # always include default custom_text
    
    category = _resolve_category(category_or_id)
    if category and "attribute_schema" in category:
        for attr in category["attribute_schema"]:
            if attr.get("type") == "text_input":
                text_keys.add(attr.get("key"))

    # Check if any text/free-text attribute has a non-empty value
    for k in text_keys:
        val = selected_attributes.get(k)
        if val is not None and str(val).strip() != "":
            return True
            
    # Fallback to key substring heuristic to be safe
    for key, val in selected_attributes.items():
        if "text" in key.lower() and val is not None and str(val).strip() != "":
            return True
            
    return False

def check_cache(category_or_id, selected_attributes):
    """
    Queries the cache for an existing configuration.
    
    Returns:
        dict: { "hit": bool, "output_image_url": str | None }
    """
    # Check if this configuration contains custom text which bypasses cache
    if is_cache_bypassed(category_or_id, selected_attributes):
        print("[Cache Service] Cache lookup bypassed due to custom text.")
        return {"hit": False, "output_image_url": None}
        
    cache_key = generate_cache_key(category_or_id, selected_attributes)
    
    try:
        cache_entry = ai_cache.find_one({"cache_key": cache_key})
        if cache_entry:
            print(f"[Cache Service] Cache HIT for key: {cache_key}")
            return {"hit": True, "output_image_url": cache_entry.get("output_image_url")}
            
        print(f"[Cache Service] Cache MISS for key: {cache_key}")
        return {"hit": False, "output_image_url": None}
    except Exception as e:
        print(f"[Cache Service] Error reading cache: {e}")
        return {"hit": False, "output_image_url": None}

def store_cache(category_or_id, selected_attributes, output_image_url):
    """Stores a successful configuration-to-image mapping in the cache database."""
    if is_cache_bypassed(category_or_id, selected_attributes):
        print("[Cache Service] Cache storage bypassed due to custom text.")
        return
        
    cache_key = generate_cache_key(category_or_id, selected_attributes)
    
    try:
        # Save to MongoDB cache collection
        ai_cache.update_one(
            {"cache_key": cache_key},
            {
                "$set": {
                    "cache_key": cache_key,
                    "category_id": category_or_id.get("category_id") if isinstance(category_or_id, dict) else category_or_id,
                    "selected_attributes": selected_attributes,
                    "output_image_url": output_image_url,
                    "created_at": datetime.datetime.utcnow()
                }
            },
            upsert=True
        )
        print(f"[Cache Service] Stored image in cache with key: {cache_key}")
    except Exception as e:
        print(f"[Cache Service] Error writing to cache: {e}")
