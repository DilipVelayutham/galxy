import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load env variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "galxy")

_client = None

def get_db_client():
    global _client
    if _client is None:
        kwargs = {"serverSelectionTimeoutMS": 5000}
        
        # Use certifi's TLS certificate bundle for secure Atlas connections if available
        if MONGO_URI.startswith("mongodb+srv://"):
            try:
                import certifi
                kwargs["tlsCAFile"] = certifi.where()
            except ImportError:
                pass
                
        _client = MongoClient(MONGO_URI, **kwargs)
    return _client

def get_db(name=None):
    client = get_db_client()
    db_name = name or DATABASE_NAME
    return client[db_name]

# Expose default database instance
db = get_db()
