import jwt
import datetime
from app.configs.jwt_config import JWTConfig

class ExpiredTokenError(Exception):
    pass

class InvalidTokenError(Exception):
    pass

def generate_access_token(user_id, role="customer"):
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=JWTConfig.JWT_ACCESS_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWTConfig.JWT_SECRET, algorithm="HS256")

def generate_refresh_token(user_id, role="customer"):
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "refresh",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=JWTConfig.JWT_REFRESH_EXPIRE_DAYS)
    }
    return jwt.encode(payload, JWTConfig.JWT_SECRET, algorithm="HS256")

def decode_token(token):
    try:
        return jwt.decode(token, JWTConfig.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError("Token has expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token signature or structure")
