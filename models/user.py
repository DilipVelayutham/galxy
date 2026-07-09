import datetime
from bson import ObjectId

def construct_user(name, email, phone, password_hash, auth_provider="email"):
    """
    Constructs a user document schema dictionary.
    """
    if not name or not email:
        raise ValueError("Name and email are required fields.")
        
    return {
        "name": name.strip(),
        "email": email.strip().lower(),
        "phone": (phone or "").strip(),
        "password_hash": password_hash,
        "addresses": [],
        "auth_provider": auth_provider,
        "is_verified": False,
        "created_at": datetime.datetime.utcnow(),
        "last_login": None
    }

def construct_admin_user(name, email, password_hash, role="super_admin"):
    """
    Constructs an admin user document schema dictionary.
    """
    if not name or not email:
        raise ValueError("Name and email are required fields.")
        
    return {
        "name": name.strip(),
        "email": email.strip().lower(),
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.datetime.utcnow()
    }

def construct_address(label, line1, line2, city, state, pincode, is_default=False):
    """
    Constructs an address schema sub-document.
    """
    if not label or not line1 or not city or not state or not pincode:
        raise ValueError("Address label, line1, city, state, and pincode are required.")
        
    return {
        "address_id": str(ObjectId()), # unique sub-document identifier
        "label": label.strip(),
        "line1": line1.strip(),
        "line2": (line2 or "").strip(),
        "city": city.strip(),
        "state": state.strip(),
        "pincode": pincode.strip(),
        "is_default": bool(is_default)
    }
