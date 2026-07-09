import logging
from functools import wraps
from flask import request, current_app
from app.config import Config
from app.utils.response_helper import error_response

logger = logging.getLogger(__name__)

def require_admin(f):
    """
    ### TEMPORARY INTEGRATION MOCK ###
    Protects admin routes by verifying the presence of a mock admin Bearer token.
    Reads ADMIN_TOKEN from current Flask app context, falling back to static config.
    
    Integration details:
        This decorator is a temporary boundary mock for Module 3. During final project integration, 
        Module 1's JWT or session validator can be swapped in place of this function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        
        # Read from current_app config if within context, fallback to static Config
        admin_token = current_app.config.get("ADMIN_TOKEN") if current_app else None
        if not admin_token:
            admin_token = Config.ADMIN_TOKEN
            
        expected_token = f"Bearer {admin_token}"
        
        if not auth_header:
            logger.warning("Access Denied: Missing Authorization header in admin request.")
            return error_response(
                message="Unauthorized. Admin credentials are required.",
                errors={"authorization": "Header is missing."},
                status_code=401
            )
            
        if auth_header != expected_token:
            logger.warning("Access Denied: Invalid admin Bearer token.")
            return error_response(
                message="Forbidden. Invalid admin credentials.",
                errors={"authorization": "Invalid token."},
                status_code=403
            )
            
        return f(*args, **kwargs)
    return decorated_function
