"""
config.py — App configuration loaded from environment variables.
All modules import settings from here; never read os.environ directly elsewhere.
"""

import os
from dotenv import load_dotenv

# Load .env file if present (dev only; production injects vars directly)
load_dotenv()


class Config:
    # ── Flask ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    DEBUG: bool = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    # ── MongoDB ───────────────────────────────────────────────────────────
    MONGO_URI: str = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.environ.get("MONGO_DB_NAME", "galaxy_pro")

    # ── Cloudinary ────────────────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.environ.get("CLOUDINARY_API_SECRET", "")

    # ── Pagination ────────────────────────────────────────────────────────
    DEFAULT_PAGE_LIMIT: int = int(os.environ.get("DEFAULT_PAGE_LIMIT", 20))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


_configs = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config() -> Config:
    """Return the config class matching FLASK_ENV (defaults to development)."""
    env = os.environ.get("FLASK_ENV", "development").lower()
    return _configs.get(env, DevelopmentConfig)
