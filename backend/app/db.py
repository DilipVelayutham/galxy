from pymongo import MongoClient
from app.config import Config

client = MongoClient(Config.MONGO_URI)

# Attempt to get default database from URI, fallback to 'galxy'
try:
    db = client.get_default_database()
    if db is None:
        db = client['galxy']
except Exception:
    db = client['galxy']
