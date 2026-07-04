from bson import ObjectId
from app.models.user import User
from app.models.address import ValidationError
from datetime import datetime

def get_profile(user_id):
    """
    Fetches the full user profile including addresses by user_id.
    """
    from app import db
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
    from app import db
    try:
        user_oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    except Exception:
        raise ValidationError({"user_id": "Invalid user ID format."})
        
    if 'email' in data:
        raise ValidationError({"email": "Email cannot be updated through the profile endpoint."})
        
    # Validate profile update fields (partial updates allowed)
    validated = User.validate_profile_data(data, partial=True)
    if not validated:
        raise ValidationError({"message": "No valid profile fields provided for update."})
        
    validated['updated_at'] = datetime.utcnow()
    
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
    
    public_dict = User.to_public_dict(user)
    # Remove sensitive fields just in case they exist
    public_dict.pop('password_hash', None)
    return public_dict
