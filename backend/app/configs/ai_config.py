import os
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

# Gemini API & AI Provider Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
MOCK_AI = os.getenv("MOCK_AI", "True").lower() in ["true", "1", "yes"]
AI_GENERATION_TIMEOUT_SECONDS = int(os.getenv("AI_GENERATION_TIMEOUT_SECONDS", "30"))

# Rate Limiting Thresholds
AI_FREE_GENERATIONS_PER_SESSION = int(os.getenv("AI_FREE_GENERATIONS_PER_SESSION", "5"))
AI_MAX_GENERATIONS_PER_USER_PER_DAY = int(os.getenv("AI_MAX_GENERATIONS_PER_USER_PER_DAY", "20"))

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://lti_platform:open123%21%40%23@ltiplat.hf8dbrx.mongodb.net/?appName=ltiplat")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "lti_hub_db")

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "dsmwxqrcz")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "615293245289625")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "ukIm85Mx3_3xeBqKSEcB4UGSxcE")
