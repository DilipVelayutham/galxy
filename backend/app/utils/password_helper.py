import bcrypt

def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt with a cost factor of 12.
    """
    if not password:
        raise ValueError("Password cannot be empty")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a bcrypt hash.
    """
    if not password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False
