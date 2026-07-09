import logging
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None

    def init_app(self, app):
        """Initializes the database client using app configuration."""
        mongo_uri = app.config.get("MONGO_URI", "mongodb://localhost:27017")
        db_name = app.config.get("DATABASE_NAME", "asil_artisan")

        try:
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[db_name]
            logger.info("Connected to MongoDB successfully.")
            self.create_required_indexes()
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e

    def create_required_indexes(self):
        """Creates indexes for reviews and testimonials collections."""
        if self.db is None:
            logger.warning("Database not initialized, skipping index creation.")
            return

        try:
            # Reviews collection indexes
            reviews = self.db["reviews"]
            reviews.create_index([("product_id", ASCENDING)])
            reviews.create_index([("is_approved", ASCENDING)])
            reviews.create_index([("user_id", ASCENDING), ("order_id", ASCENDING)])
            reviews.create_index([("created_at", ASCENDING)])
            logger.info("Database indexes for reviews created successfully.")
            
            # Testimonials collection indexes
            testimonials = self.db["testimonials"]
            testimonials.create_index([("is_active", ASCENDING)])
            testimonials.create_index([("display_order", ASCENDING)])
            testimonials.create_index([("is_active", ASCENDING), ("display_order", ASCENDING)])
            logger.info("Database indexes for testimonials created successfully.")
        except Exception as e:
            logger.error(f"Error creating database indexes: {e}")

    def get_collection(self, name):
        """Returns a collection handle, or None if connection is not initialized."""
        if self.db is not None:
            return self.db[name]
        return None

# Singleton database instance
db = Database()
