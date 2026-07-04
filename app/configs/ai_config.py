import os

class AIConfig:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/galxy")
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
    AI_GENERATION_TIMEOUT_SECONDS = int(os.getenv("AI_GENERATION_TIMEOUT_SECONDS", "30"))
    
    # Quota & Rate Limiting Configurations (for integration with Gokul's task)
    AI_FREE_GENERATIONS_PER_SESSION = int(os.getenv("AI_FREE_GENERATIONS_PER_SESSION", "5"))
    AI_MAX_GENERATIONS_PER_USER_PER_DAY = int(os.getenv("AI_MAX_GENERATIONS_PER_USER_PER_DAY", "20"))
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
