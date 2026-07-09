import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Flask application configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-flask-secret-key-galxy')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # MongoDB Configuration
    MONGO_URI = os.environ.get('MONGO_URI')
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'galxy')
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')
    
    # JWT Secret for require_admin decorator
    JWT_SECRET = os.environ.get('JWT_SECRET', 'super_secret_jwt_key_for_galxy_cms')

    # CORS Configuration
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')

    # Media Validation Constants (From Module 10B)
    DEFAULT_FOLDER = "galxy/general"
    VALID_FOLDERS = {
        "galxy/products",
        "galxy/categories",
        "galxy/site-content",
        "galxy/reviews",
        "galxy/ai-previews",
        "galxy/general"
    }
    ALLOWED_FORMATS = {"jpg", "jpeg", "png", "webp"}
    ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
    MAX_FILE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # 5 MB
    MAX_CONTENT_LENGTH = (MAX_FILE_SIZE_MB + 1) * 1024 * 1024  # 6 MB request payload limit

