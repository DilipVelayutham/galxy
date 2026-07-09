import os
from pymongo import MongoClient

_client = None
_db = None

def init_db(app=None, testing=False, mock_client=None):
    """
    Initializes the database connection.
    Can be configured with a mock client or testing mode.
    """
    global _client, _db
    if mock_client is not None:
        _client = mock_client
        _db = _client.get_database("galaxy_test")
        return _db
        
    if testing:
        import mongomock
        _client = mongomock.MongoClient()
        _db = _client.get_database("galaxy_test")
        return _db

    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/galaxy")
    db_name = os.environ.get("MONGO_DB_NAME", "galaxy")
    _client = MongoClient(mongo_uri)
    _db = _client[db_name]
    return _db

def get_db():
    """
    Returns the initialized database instance.
    """
    global _db
    if _db is None:
        init_db()
    return _db
