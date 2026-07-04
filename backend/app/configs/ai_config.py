<<<<<<< HEAD
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
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is required but missing.")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "lti_hub_db")

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
    raise ValueError("Cloudinary configuration environment variables (CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET) are required but missing.")
=======
"""
ai_config.py — Module 5 AI Preview Generation
Configuration loader for all AI-related settings.
Reads from environment variables / .env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── AI Provider ────────────────────────────────────────────────────────────────
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ─── Rate Limit Thresholds ───────────────────────────────────────────────────────
# Guests (session_id based): hard cap per session across all time.
AI_FREE_GENERATIONS_PER_SESSION: int = int(
    os.getenv("AI_FREE_GENERATIONS_PER_SESSION", "5")
)
# Logged-in users: daily cap (resets at midnight UTC).
AI_MAX_GENERATIONS_PER_USER_PER_DAY: int = int(
    os.getenv("AI_MAX_GENERATIONS_PER_USER_PER_DAY", "20")
)

# ─── Provider Timeout ────────────────────────────────────────────────────────────
AI_GENERATION_TIMEOUT_SECONDS: int = int(
    os.getenv("AI_GENERATION_TIMEOUT_SECONDS", "30")
)

# ─── Cloudinary ──────────────────────────────────────────────────────────────────
CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
CLOUDINARY_AI_PREVIEW_FOLDER: str = "galxy/ai-previews"

# ─── MongoDB ─────────────────────────────────────────────────────────────────────
MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/galxy")
DB_NAME: str = os.getenv("DB_NAME", "galxy")

# ─── Module Integration URLs ─────────────────────────────────────────────────────
MODULE4_VALIDATE_URL: str = os.getenv(
    "MODULE4_VALIDATE_URL",
    "http://localhost:5004/api/internal/validate-attributes",
)
>>>>>>> origin/main
