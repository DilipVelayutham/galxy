"""
auth_helpers.py — Module 5 authentication decorators
Reuse Module 1's auth patterns. This is a compatibility shim that reads
JWTs from the Authorization header.

Per spec: Module 1 owns auth — pull Module 1's decorators directly once
they're pushed to the dev branch. This shim ensures Module 5 can develop
in isolation while Module 1 is being built.

Decorators provided:
  @optional_auth  — extracts user_id/is_admin from JWT if present; continues
                    if no token (guest flow).
  @require_auth   — returns 401 if no valid JWT.
  @require_admin  — returns 403 if not admin.
"""
import os
import logging
from functools import wraps
from flask import request, jsonify, g
from jose import jwt, JWTError

logger = logging.getLogger(__name__)
JWT_SECRET = os.getenv("JWT_SECRET", "changeme_jwt_secret_here")
JWT_ALGORITHM = "HS256"


def _extract_user_from_token() -> tuple[str | None, bool]:
    """
    Parse the Authorization: Bearer <token> header.
    Returns (user_id, is_admin) or (None, False) if no/invalid token.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, False
    token = auth_header[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub") or payload.get("user_id")
        is_admin = payload.get("is_admin", False)
        return user_id, bool(is_admin)
    except JWTError as exc:
        logger.debug("JWT decode failed: %s", exc)
        return None, False


def optional_auth(fn):
    """
    Decorator: attempt JWT extraction. Sets g.user_id and g.is_admin.
    Never rejects requests — guests pass through with user_id=None.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        g.user_id, g.is_admin = _extract_user_from_token()
        return fn(*args, **kwargs)
    return wrapper


def require_auth(fn):
    """
    Decorator: require a valid JWT. Returns 401 if absent or invalid.
    Sets g.user_id and g.is_admin on success.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id, is_admin = _extract_user_from_token()
        if not user_id:
            return jsonify({"success": False, "message": "Authentication required."}), 401
        g.user_id = user_id
        g.is_admin = is_admin
        return fn(*args, **kwargs)
    return wrapper


def require_admin(fn):
    """
    Decorator: require a valid JWT with is_admin=True. Returns 403 otherwise.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id, is_admin = _extract_user_from_token()
        if not user_id:
            return jsonify({"success": False, "message": "Authentication required."}), 401
        if not is_admin:
            return jsonify({"success": False, "message": "Admin access required."}), 403
        g.user_id = user_id
        g.is_admin = is_admin
        return fn(*args, **kwargs)
    return wrapper
