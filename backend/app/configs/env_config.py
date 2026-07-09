import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # MongoDB
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "galxy_db")

    # JWT Authentication
    JWT_SECRET = os.environ.get("JWT_SECRET", "default_jwt_secret_key_change_me")
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
    DB_NAME = os.environ.get("DB_NAME", "reviews_db")

    # Flask Configuration
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
