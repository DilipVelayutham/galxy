import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
    SECRET_KEY = os.environ.get("SECRET_KEY", "reviews_backend_secret_key_999")
    
    # MongoDB Configuration
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/reviews_db")
    DB_NAME = os.environ.get("DB_NAME", "reviews_db")
    
    # JWT Configuration
    JWT_SECRET = os.environ.get("JWT_SECRET", "default_jwt_secret_key_12345")
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
    
    PORT = int(os.environ.get("PORT", 5000))
