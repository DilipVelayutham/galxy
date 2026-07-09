import logging
from pymongo import MongoClient, ASCENDING, TEXT
from app.config import Config

from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.client = None
        self.db = None

    def init_app(self, app):
        """
        Initializes the MongoDB connection using Flask config or Config variables.
        """
        uri = Config.MONGO_URI
        db_name = Config.MONGO_DB_NAME
        
        if not uri:
            logger.error("MONGO_URI not configured in environment!")
            raise ValueError("MONGO_URI is missing from environment variables.")
        
        try:
            logger.info(f"Connecting to MongoDB Atlas database: {db_name}")
            # Use 5 seconds selection timeout to fail fast if IP is not whitelisted
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[db_name]
            
            # Verify connection using ping command
            self.db.command('ping')
            logger.info("MongoDB Atlas connection established successfully.")
            
            # Ensure indexes exist
            self.create_indexes()
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            logger.critical(
                "\n" + "="*80 +
                "\n[DATABASE CONNECTION ERROR]"
                "\nFailed to connect to the MongoDB Atlas cluster."
                f"\nDetails: {e}"
                "\n"
                "\nThis error is most commonly caused by MongoDB Atlas IP Whitelisting rules."
                "\n"
                "\nTo resolve this:"
                "\n1. Log in to your MongoDB Atlas Console."
                "\n2. In 'Security' -> 'Network Access', click 'Add IP Address'."
                "\n3. Add your current IP address, or enter '0.0.0.0/0' to temporarily"
                "\n   allow connections from anywhere for testing."
                "\n" + "="*80 + "\n"
            )
            raise e


    def create_indexes(self):
        """
        Creates all indexes for the products collection as required by the specifications:
        - slug: Unique index
        - category_id: Filter index
        - tags: Multikey filter index
        - is_active, is_featured: Compound filter index
        - title + description: Text index for search
        """
        if self.db is None:
            logger.error("Database connection not initialized. Cannot create indexes.")
            return
            
        try:
            products = self.db.products
            
            # 1. Unique index on slug
            products.create_index("slug", unique=True)
            logger.info("Unique index on 'slug' verified/created.")
            
            # 2. Filter index on category_id
            products.create_index("category_id")
            logger.info("Filter index on 'category_id' verified/created.")
            
            # 3. Filter indexes on tags, is_active, is_featured
            products.create_index("tags")
            products.create_index([("is_active", ASCENDING), ("is_featured", ASCENDING)])
            logger.info("Filter indexes on 'tags' and 'is_active'/'is_featured' verified/created.")
            
            # 4. Text index on title and description for search
            products.create_index([
                ("title", TEXT),
                ("description", TEXT)
            ], weights={
                "title": 10,
                "description": 2
            }, name="product_search_text_index")
            logger.info("Text search index on 'title' and 'description' verified/created.")
            
        except Exception as e:
            logger.error(f"Error creating MongoDB indexes: {e}")

# Singleton database connection wrapper
db_conn = DatabaseConnection()
