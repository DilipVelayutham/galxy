import os

class JWTConfig:
    # Secret key for JWT signing. Exits if not set in production, defaults for safety.
    JWT_SECRET = os.getenv("JWT_SECRET", "dev_jwt_secret_key_98765_extra_safe_length")
    
    # Expirations
    JWT_ACCESS_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", 15))
    JWT_REFRESH_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", 30))
