import os
import logging
from flask import jsonify

logger = logging.getLogger(__name__)

# Unify FLASK_ENV checks for all admin/media routes
FLASK_ENV = os.environ.get("FLASK_ENV", "development").lower()

if FLASK_ENV in ["development", "testing"]:
    # Import from the development stub
    from app.utils._dev_auth_stub import require_admin
else:
    # Production/Staging: Strictly require production auth.
    # Since Module 1 real auth is not in this workspace, we define a secure fallback
    # that rejects unauthorized access by default.
    def require_admin(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            return jsonify({
                "success": False,
                "message": "Unauthorized. Production authentication middleware is not configured.",
                "errors": {"auth": "Production authentication required"}
            }), 401
        return decorated
