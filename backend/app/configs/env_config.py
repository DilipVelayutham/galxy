import os
from app.config import Config as MainConfig

class Config(MainConfig):
    # MongoDB - fallback to MainConfig
    MONGO_URI = os.environ.get("MONGO_URI", MainConfig.MONGO_URI)
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "galxy")

    # JWT Authentication
    JWT_SECRET = os.environ.get("JWT_SECRET", MainConfig.JWT_SECRET)

    # Flask Configuration
    FLASK_ENV = os.environ.get("FLASK_ENV", MainConfig.ENV)
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "1" if MainConfig.DEBUG else "0") == "1"
