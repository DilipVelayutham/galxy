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
    
    # JWT Configuration
    JWT_SECRET = os.getenv("JWT_SECRET", "dev_jwt_secret_key_98765_extra_safe_length")
    SECRET_KEY = os.getenv("SECRET_KEY", "default-flask-secret-key-galxy")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
    AI_FREE_GENERATIONS_PER_SESSION = int(os.getenv("AI_FREE_GENERATIONS_PER_SESSION", "3"))

    # SMTP Configuration
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

