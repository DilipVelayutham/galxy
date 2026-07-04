import pymongo
from app.configs.ai_config import MONGO_URI, MONGO_DB_NAME

# Setup PyMongo client
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Collections
categories = db["categories"]
ai_generations = db["ai_generations"]
ai_cache = db["ai_cache"]

def get_db():
    return db

def init_indexes():
    """Initializes standard indexes on collections for optimized queries."""
    try:
        # Generations indexes
        ai_generations.create_index("user_id")
        ai_generations.create_index("session_id")
        ai_generations.create_index("category_id")
        ai_generations.create_index("created_at")
        
        # Cache index
        ai_cache.create_index("cache_key", unique=True)
        
        # Categories index
        categories.create_index("category_id", unique=True, sparse=True)
        categories.create_index("slug", unique=True, sparse=True)
        print("MongoDB indexes created successfully.")
    except Exception as e:
        print(f"Error creating MongoDB indexes: {e}")
