"""
db.py — Shared MongoDB connection for Module 5 backend.
Single connection instance reused across all requests.
"""
from pymongo.database import Database
from app.database import db as shared_db


def get_db() -> Database:
    """Return the shared MongoDB database instance."""
    return shared_db


def close_db():
    """No-op wrapper for close_db."""
    pass

