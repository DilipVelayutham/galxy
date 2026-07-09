import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = FLASK_ENV == "development"
    
    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "galxy_db")
    
    # Cloudinary configuration URL
    CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
    
    # Secret token for the temporary admin integration mock
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "mock-admin-token-12345")
