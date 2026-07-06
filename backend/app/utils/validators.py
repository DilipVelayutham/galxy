import re

def validate_email(email):
    """
    Validates standard email format and returns (is_valid, normalized_email_or_error_msg).
    """
    if not email:
        return False, "Email is required"
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, email

def validate_password(password):
    """
    Validates password strength (min 8 chars, 1 letter, 1 number) and returns (is_valid, password_or_error_msg).
    """
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, password

def validate_phone(phone):
    """
    Validates 10-digit Indian mobile number format and returns (is_valid, phone_or_error_msg).
    """
    if not phone:
        return False, "Phone number is required"
    phone = str(phone).strip()
    pattern = r'^[6-9]\d{9}$'
    if not re.match(pattern, phone):
        return False, "Phone must be a valid 10-digit Indian mobile number"
    return True, phone

def validate_pincode(pincode):
    """
    Validates 6-digit numeric pincode and returns (is_valid, pincode_or_error_msg).
    """
    if not pincode:
        return False, "Pincode is required"
    pincode = str(pincode).strip()
    pattern = r'^\d{6}$'
    if not re.match(pattern, pincode):
        return False, "Pincode must be a 6-digit numeric code"
    return True, pincode
