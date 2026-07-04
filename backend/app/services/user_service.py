from bson import ObjectId
from app.db import get_db
from app.models.user import User

class UserServiceError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class UserService:
    @staticmethod
    def get_profile(user_id):
        """
        Retrieves the full profile of a user (excluding password_hash).
        """
        db = get_db()
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise UserServiceError("User not found", 404)
        return User.to_public_dict(user)

    @staticmethod
    def get_public_profile(user_id):
        """
        Returns display-only info safe for external lookup by other modules.
        Omit password_hash and addresses.
        """
        db = get_db()
        user = db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0, "addresses": 0})
        if not user:
            raise UserServiceError("User not found", 404)
        return User.to_public_dict(user)
