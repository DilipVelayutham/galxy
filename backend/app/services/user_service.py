from bson import ObjectId
from app.models.user import validate_profile_data, to_public_dict
from app.models.address import ValidationError
from datetime import datetime, timezone
from app.db import db

def get_profile(user_id):
    """
    Fetches the full user profile including addresses by user_id.
    """
    # db import moved to top
    try:
        user_oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    except Exception:
        return None
        
    user = db.users.find_one({"_id": user_oid})
    return user

def update_profile(user_id, data):
    """
    Updates a user's profile fields. Accepts name and phone only.
    Rejects the request if 'email' is present.
    """
    # db import moved to top
    try:
        user_oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    except Exception:
        raise ValidationError({"user_id": "Invalid user ID format."})
        
    if 'email' in data:
        raise ValidationError({"email": "Email cannot be updated through the profile endpoint."})
        
    # Validate profile update fields (partial updates allowed)
    validated = validate_profile_data(data, partial=True)
    if not validated:
        raise ValidationError({"message": "No valid profile fields provided for update."})
        
    validated['updated_at'] = datetime.now(timezone.utc)
    
    user = db.users.find_one_and_update(
        {"_id": user_oid},
        {"$set": validated},
        return_document=True
    )
    if not user:
        raise ValidationError({"message": "User not found."})
        
    return user

def get_public_profile(user_id):
    """
    Returns only public-facing safe profile details for other modules.
    Guarantees that sensitive data like password_hash is never exposed.
    """
    user = get_profile(user_id)
    if not user:
        return None
    
    public_dict = to_public_dict(user)
    # Remove sensitive fields just in case they exist
    public_dict.pop('password_hash', None)
    return public_dict
