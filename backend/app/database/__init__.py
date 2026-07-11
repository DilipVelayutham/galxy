from app.db import get_db

def __getattr__(name):
    if name == 'get_db':
        return get_db
    
    # Map specific collections to their actual MongoDB names
    collection_mapping = {
        "categories": "m5_categories",
        "ai_generations": "m5_generations",
        "ai_cache": "m5_cache"
    }
    col_name = collection_mapping.get(name, name)
    return get_db()[col_name]

def init_indexes():
    """Initializes standard indexes on collections for optimized queries."""
    try:
        db = get_db()
        db["m5_generations"].create_index("user_id")
        db["m5_generations"].create_index("session_id")
        db["m5_generations"].create_index("category_id")
        db["m5_generations"].create_index("created_at")
        
        db["m5_cache"].create_index("cache_key", unique=True)
        
        db["m5_categories"].create_index("category_id", unique=True, sparse=True)
        db["m5_categories"].create_index("slug", unique=True, sparse=True)
        print("MongoDB indexes created successfully.")
    except Exception as e:
        print(f"Error creating MongoDB indexes: {e}")

