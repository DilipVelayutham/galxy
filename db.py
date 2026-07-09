import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch MongoDB configurations from environment variables or use default values
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "cart_db")

# Initialize client and database
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

def init_all_indexes():
    """
    Creates unique and lookup indexes for all primary GALXY collections.
    """
    try:
        # Users indexes
        db.users.create_index("email", unique=True)
        
        # Admin Users indexes
        db.admin_users.create_index("email", unique=True)
        
        # Categories indexes
        db.categories.create_index("slug", unique=True)
        
        # Products indexes
        db.products.create_index("slug", unique=True)
        db.products.create_index("category_id")
        
        # Carts indexes
        db.carts.create_index("user_id", unique=True)
        
        # Orders indexes
        db.orders.create_index("order_number", unique=True)
        db.orders.create_index("user_id")
        
        print("MongoDB indexes initialized successfully.")
    except Exception as e:
        print(f"Error initializing MongoDB indexes: {e}")
