import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ENV = os.environ.get("ENV", "development")
    DEBUG = ENV == "development"
    PORT = int(os.environ.get("PORT", 5000))
    
    # MongoDB Config
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/galxy")
    
    # JWT Config
    JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-dev-key")
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Cloudinary Config
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")
    
    # Gemini API Config
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
