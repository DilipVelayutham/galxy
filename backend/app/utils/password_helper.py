import bcrypt

def hash_password(plain_password: str) -> str:
    """
    Hashes a plain text password using bcrypt with a cost factor of 12.
    """
    if not plain_password:
        raise ValueError("Password cannot be empty")
        
    password_bytes = plain_password.encode('utf-8')
    # Generate a salt with work factor 12
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verifies a plain text password against a bcrypt hash in constant time.
    """
    if not plain_password or not password_hash:
        return False
        
    try:
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        # Prevent any potential timing/decoding exceptions from exposing logic
        return False
