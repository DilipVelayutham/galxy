"""
db.py — Shared MongoDB connection for Module 5 backend.
Single connection instance reused across all requests.
"""
from pymongo import MongoClient
from pymongo.database import Database
from app.configs.ai_config import MONGO_URI, DB_NAME

_client: MongoClient | None = None
_db: Database | None = None


def get_db() -> Database:
    """Return the singleton MongoDB database instance."""
    global _client, _db
    if _db is None:
        _client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
        )
        _db = _client[DB_NAME]
    return _db


def close_db():
    """Close the MongoDB connection (call on app teardown)."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
