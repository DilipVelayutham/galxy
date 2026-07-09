from app.database.db import db
from app.configs.env_config import Config

def init_indexes():
    """Delegated to the central Database.create_required_indexes."""
    if db.db is not None:
        db.create_required_indexes()

def init_db(uri=None, db_name=None, force=False):
    """Initializes PyMongo connection, supporting mongomock for test runtimes."""
    if db.db is not None and not force:
        return db.db

    mongo_uri = uri or Config.MONGO_URI or ""
    
    if Config.FLASK_ENV == "testing" or mongo_uri.startswith("mongomock://"):
        import mongomock
        db.client = mongomock.MongoClient()
        db.db = db.client[db_name or "test_reviews_db"]
    else:
        # Fallback to standard initialization if client is not set
        from pymongo import MongoClient
        db.client = MongoClient(mongo_uri)
        db.db = db.client[db_name or Config.DATABASE_NAME]

    init_indexes()
    return db.db

def get_db():
    """Gets the database instance, initializing if necessary."""
    if db.db is None:
        return init_db()
    return db.db

def get_reviews_col():
    """Gets the reviews collection."""
    return get_db()["reviews"]
