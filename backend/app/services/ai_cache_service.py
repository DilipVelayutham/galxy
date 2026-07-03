import hashlib
import json
import datetime
from bson import ObjectId
from app.database import ai_cache

def generate_cache_key(category_id, selected_attributes):
    """
    Generates a deterministic SHA256 hash key for caching.
    Sorts attributes alphabetically by key to prevent key-order misses.
    Computes SHA256(category_id + sorted_alphabetic(selected_attributes))
    """
    cat_str = str(category_id)
    
    # Sort selected_attributes alphabetically by key
    sorted_keys = sorted(selected_attributes.keys())
    
    # Concatenate alphabetically: category_id + key1:val1 + key2:val2 ...
    attrs_str = "".join(
        f"{k}:{selected_attributes[k]}"
        for k in sorted_keys
        if selected_attributes[k] is not None and str(selected_attributes[k]).strip() != ""
    )
    
    combined_string = f"{cat_str}:{attrs_str}"
    sha256 = hashlib.sha256(combined_string.encode('utf-8'))
    return sha256.hexdigest()

def is_cache_bypassed(selected_attributes):
    """
    Returns True if the payload contains custom_text or free text selections,
    which bypasses the cache lookup and storage entirely.
    """
    # Any custom_text value bypasses cache lookup/storage (unique designs)
    custom_text_val = selected_attributes.get("custom_text")
    if custom_text_val is not None and str(custom_text_val).strip() != "":
        return True
        
    # Check for generic text input fields in selected attributes
    for key, val in selected_attributes.items():
        if "text" in key.lower() and val is not None and str(val).strip() != "":
            return True
            
    return False

def check_cache(category_id, selected_attributes):
    """
    Queries the cache for an existing configuration.
    
    Returns:
        dict: { "hit": bool, "output_image_url": str | None }
    """
    # Check if this configuration contains custom text which bypasses cache
    if is_cache_bypassed(selected_attributes):
        print("[Cache Service] Cache lookup bypassed due to custom text.")
        return {"hit": False, "output_image_url": None}
        
    cache_key = generate_cache_key(category_id, selected_attributes)
    
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

def store_cache(category_id, selected_attributes, output_image_url):
    """Stores a successful configuration-to-image mapping in the cache database."""
    if is_cache_bypassed(selected_attributes):
        print("[Cache Service] Cache storage bypassed due to custom text.")
        return
        
    cache_key = generate_cache_key(category_id, selected_attributes)
    
    try:
        # Save to MongoDB cache collection
        ai_cache.update_one(
            {"cache_key": cache_key},
            {
                "$set": {
                    "cache_key": cache_key,
                    "category_id": category_id,
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
