import re

def validate_email(email: str) -> tuple[bool, str]:
    """
    Validates standard email format and returns (is_valid, normalized_email_or_error).
    If valid, normalized_email_or_error will contain the lowercase normalized email.
    """
    if not email:
        return False, "Email is required"
    
    email = email.strip()
    # General email format regex matching standard email strings
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False, "Invalid email format"
        
    return True, email.lower()

def validate_password(password: str) -> tuple[bool, str]:
    """
    Enforces password rules: min 8 characters, at least one letter, and one number.
    Returns (is_valid, error_message). On success, error_message is empty.
    """
    if not password:
        return False, "Password is required"
        
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
        
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter"
        
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
        
    return True, ""

def validate_phone(phone: str) -> tuple[bool, str]:
    """
    Enforces 10-digit Indian mobile number format.
    Returns (is_valid, phone_or_error). On success, phone_or_error is the stripped phone number.
    """
    if not phone:
        return False, "Phone number is required"
        
    phone = phone.strip()
    # 10-digit Indian mobile format starts with 6, 7, 8, or 9
    phone_regex = r'^[6-9]\d{9}$'
    if not re.match(phone_regex, phone):
        return False, "Phone number must be a valid 10-digit Indian mobile number"
        
    return True, phone

def validate_pincode(pincode: str) -> tuple[bool, str]:
    """
    Enforces 6-digit numeric pincode format.
    Returns (is_valid, pincode_or_error). On success, pincode_or_error is the stripped pincode.
    """
    if not pincode:
        return False, "Pincode is required"
        
    pincode = pincode.strip()
    # 6-digit numeric pincode regex
    pincode_regex = r'^\d{6}$'
    if not re.match(pincode_regex, pincode):
        return False, "Pincode must be exactly 6 digits"
        
    return True, pincode
