import logging
from app.db import db as main_db

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Delegate directly to the main database client and instance
        self.client = main_db.client
        self.db = main_db

    def init_app(self, app):
        """Initializes the database client using app configuration."""
        # Main db is statically initialized on import, so we only run index creation here
        self.create_required_indexes()

    def create_required_indexes(self):
        """Creates indexes for testimonials collection to optimize query performance."""
        if self.db is None:
            logger.warning("Database not initialized, skipping index creation.")
            return

        try:
            testimonials = self.db["testimonials"]
            from pymongo import ASCENDING
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
