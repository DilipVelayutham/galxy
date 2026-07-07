import re
from datetime import datetime, timezone
from bson import ObjectId
from app.models.address import ValidationError

def validate_phone(phone):
    if not phone:
        return False
    # 10-digit Indian mobile format (starts with 6-9 and has 10 digits total)
    return bool(re.match(r'^[6-9]\d{9}$', str(phone).strip()))

def validate_email(email):
    if not email:
        return False
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', str(email).strip().lower()))

def validate_profile_data(data, partial=False):
    errors = {}
    
    if 'name' in data or not partial:
        name = data.get('name')
        if name is None or not str(name).strip():
            errors['name'] = "Name is required."
            
    if 'phone' in data:
        phone = data.get('phone')
        # if updating, it shouldn't be empty, and must match mobile format
        if phone is None or not str(phone).strip():
            errors['phone'] = "Phone is required."
        elif not validate_phone(phone):
            errors['phone'] = "Phone must be a valid 10-digit Indian mobile number."
            
    if 'email' in data:
        email = data.get('email')
        if email is None or not str(email).strip():
            errors['email'] = "Email is required."
        elif not validate_email(email):
            errors['email'] = "Email must be a valid email address."
            
    if errors:
        raise ValidationError(errors)
        
    validated = {}
    if 'name' in data:
        validated['name'] = str(data['name']).strip()
    if 'phone' in data:
        validated['phone'] = str(data['phone']).strip()
    if 'email' in data:
        validated['email'] = str(data['email']).strip().lower()
        
    return validated

def to_public_dict(user):
    """
    Returns a safe dictionary representation of the user,
    stripping out password_hash and other sensitive details.
    """
    if not user:
        return None
        
    addresses = []
    for addr in user.get('addresses', []):
        addresses.append({
            "_id": str(addr['_id']) if isinstance(addr.get('_id'), ObjectId) else addr.get('_id'),
            "label": addr.get('label', ''),
            "line1": addr.get('line1', ''),
            "line2": addr.get('line2', ''),
            "city": addr.get('city', ''),
            "state": addr.get('state', ''),
            "pincode": addr.get('pincode', ''),
            "is_default": addr.get('is_default', False)
        })
        
    return {
        "_id": str(user['_id']) if isinstance(user.get('_id'), ObjectId) else user.get('_id'),
        "name": user.get('name', ''),
        "email": user.get('email', ''),
        "phone": user.get('phone', ''),
        "addresses": addresses,
        "auth_provider": user.get('auth_provider', 'email'),
        "is_verified": user.get('is_verified', False),
        "is_active": user.get('is_active', True),
        "created_at": user.get('created_at').isoformat() if isinstance(user.get('created_at'), datetime) else user.get('created_at'),
        "updated_at": user.get('updated_at').isoformat() if isinstance(user.get('updated_at'), datetime) else user.get('updated_at'),
        "last_login": user.get('last_login').isoformat() if isinstance(user.get('last_login'), datetime) else user.get('last_login')
    }

class User:
    @staticmethod
    def create_document(name, email, phone, password_hash, auth_provider="email"):
        """
        Creates a dictionary representation of a user document.
        """
        now = datetime.now(timezone.utc)
        return {
            "name": name,
            "email": email.strip().lower(),
            "phone": phone.strip() if phone else "",
            "password_hash": password_hash,
            "addresses": [],
            "auth_provider": auth_provider,
            "is_verified": False,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "last_login": None
        }

    @staticmethod
    def to_public_dict(user_doc):
        """
        Returns a user document representation safe for public exposure.
        Delegates to the module-level to_public_dict function.
        """
        return to_public_dict(user_doc)
