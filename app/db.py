import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import Config

logger = logging.getLogger(__name__)

class Database:
    _client = None
    _db = None
    _is_mock = False

    @classmethod
    def get_client(cls):
        """Get or initialize the MongoClient instance."""
        if cls._client is None:
            from flask import current_app, has_app_context
            if has_app_context():
                uri = current_app.config.get('MONGO_URI')
            else:
                uri = Config.MONGO_URI
            
            # Check if URI indicates a mock or if we are in testing
            if not uri or "mock" in uri.lower():
                logger.warning("Mock MongoDB requested. Setting up in-memory mongomock client...")
                import mongomock
                cls._client = mongomock.MongoClient()
                cls._is_mock = True
                return cls._client

            try:
                # Mask password in logs
                masked_uri = uri
                if "@" in uri:
                    parts = uri.split("@")
                    prefix = parts[0].split("://")
                    protocol = prefix[0]
                    domain = parts[1]
                    masked_uri = f"{protocol}://<credentials>@{domain}"
                
                logger.info(f"Connecting to MongoDB with URI: {masked_uri}")
                # Timeout after 3 seconds for local fallback or fast failure
                import certifi
                cls._client = MongoClient(uri, serverSelectionTimeoutMS=3000, tlsCAFile=certifi.where())
                # Ping to verify active connection
                cls._client.admin.command('ping')
                logger.info("Successfully connected to live MongoDB cluster.")
                cls._is_mock = False
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.warning(f"Failed to connect to live MongoDB: {e}")
                logger.warning("Falling back to in-memory mongomock Client...")
                import mongomock
                cls._client = mongomock.MongoClient()
                cls._is_mock = True
            except Exception as e:
                logger.error(f"Unexpected error when connecting to MongoDB: {e}")
                raise e
        return cls._client

    @classmethod
    def get_db(cls):
        """Get the database instance."""
        if cls._db is None:
            client = cls.get_client()
            from flask import current_app, has_app_context
            if has_app_context():
                db_name = current_app.config.get('MONGO_DB_NAME', Config.MONGO_DB_NAME)
            else:
                db_name = Config.MONGO_DB_NAME
            cls._db = client[db_name]
        return cls._db

    @classmethod
    def init_db(cls):
        """Initialize database constraints."""
        logger.info("Initializing database constraints...")
        from app.models.site_content import ensure_indexes
        ensure_indexes()

def get_db():
    return Database.get_db()
