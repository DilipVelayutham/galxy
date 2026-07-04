import pymongo
from app.config import Config

_client = None
_db = None

def init_indexes():
    """Initializes MongoDB indexes for reviews and testimonials."""
    global _db
    if _db is None:
        return
    try:
        # Index on product_id
        _db["reviews"].create_index([("product_id", 1)])
        # Index on is_approved
        _db["reviews"].create_index([("is_approved", 1)])
        # Compound index on user_id + order_id
        _db["reviews"].create_index([("user_id", 1), ("order_id", 1)])
        # Index on created_at
        _db["reviews"].create_index([("created_at", 1)])
        
        # Testimonials collection indexes
        _db["testimonials"].create_index([("is_active", 1)])
        _db["testimonials"].create_index([("display_order", 1)])
        
        print("[DATABASE] MongoDB indexes initialized successfully.")
    except Exception as e:
        print(f"[DATABASE] Index initialization warning: {e}")

def init_db(uri=None, db_name=None, force=False):
    """Initializes PyMongo connection or mongomock client for testing."""
    global _client, _db
    if _db is not None and not force:
        return _db
        
    uri = uri or Config.MONGO_URI
    db_name = db_name or Config.DB_NAME
    
    if Config.FLASK_ENV == "testing" or uri.startswith("mongomock://"):
        import mongomock
        _client = mongomock.MongoClient()
        _db = _client[db_name]
    else:
        _client = pymongo.MongoClient(uri)
        _db = _client[db_name]
        
    init_indexes()
    return _db

def get_db():
    """Gets the database instance, initializing if necessary."""
    global _db
    if _db is None:
        return init_db()
    return _db

def get_reviews_col():
    """Gets the reviews collection."""
    return get_db()["reviews"]
