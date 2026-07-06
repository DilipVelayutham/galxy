import os
import sys
import unittest
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

# Ensure backend root is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create a minimal Flask app for testing routes
from flask import Flask
from app.routes.auth_routes import auth_bp

class TestPasswordHelper(unittest.TestCase):
    def test_hashing_and_verification(self):
        from app.utils.password_helper import hash_password, verify_password
        
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        # 1. Verify bcrypt format ($2b$12$)
        self.assertTrue(hashed.startswith("$2b$12$"))
        
        # 2. Verify correctness
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword123!", hashed))
        self.assertFalse(verify_password(password, "another_hash"))

    def test_empty_password(self):
        from app.utils.password_helper import hash_password
        with self.assertRaises(ValueError):
            hash_password("")


class TestValidators(unittest.TestCase):
    def test_email_validation(self):
        from app.utils.validators import validate_email
        
        # Valid cases
        valid_cases = ["test@example.com", "user.name+tag@domain.co.in", "  TrimmedEmail@test.com  "]
        for case in valid_cases:
            is_valid, val = validate_email(case)
            self.assertTrue(is_valid, f"Failed on valid: {case}")
            self.assertEqual(val, case.strip().lower())
            
        # Invalid cases
        invalid_cases = ["", "plainaddress", "@missing-local.org", "user@.missing-sld"]
        for case in invalid_cases:
            is_valid, _ = validate_email(case)
            self.assertFalse(is_valid, f"Passed on invalid: {case}")

    def test_password_validation(self):
        from app.utils.validators import validate_password
        
        # Valid: min 8, 1 letter, 1 number
        self.assertTrue(validate_password("pass12345")[0])
        self.assertTrue(validate_password("Secure1!")[0])
        
        # Invalid
        self.assertFalse(validate_password("short1")[0])  # < 8 chars
        self.assertFalse(validate_password("12345678")[0])  # no letter
        self.assertFalse(validate_password("nonumberpwd")[0])  # no number
        self.assertFalse(validate_password("")[0])

    def test_phone_validation(self):
        from app.utils.validators import validate_phone
        
        # Valid Indian mobiles (10 digits starting with 6-9)
        self.assertTrue(validate_phone("9876543210")[0])
        self.assertTrue(validate_phone("6789012345")[0])
        
        # Invalid
        self.assertFalse(validate_phone("5555555555")[0])  # starts with 5
        self.assertFalse(validate_phone("987654321")[0])   # 9 digits
        self.assertFalse(validate_phone("98765432100")[0])  # 11 digits
        self.assertFalse(validate_phone("abc1234567")[0])   # letters
        self.assertFalse(validate_phone("")[0])

    def test_pincode_validation(self):
        from app.utils.validators import validate_pincode
        
        # Valid: 6-digit numeric
        self.assertTrue(validate_pincode("600001")[0])
        self.assertTrue(validate_pincode("110011")[0])
        
        # Invalid
        self.assertFalse(validate_pincode("12345")[0])    # 5 digits
        self.assertFalse(validate_pincode("1234567")[0])  # 7 digits
        self.assertFalse(validate_pincode("12a456")[0])   # contains letter
        self.assertFalse(validate_pincode("")[0])


class TestAuthService(unittest.TestCase):
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.send_reset_email')
    def test_forgot_password_user_exists(self, mock_send_email, mock_db):
        from app.services.auth_service import forgot_password
        
        # Setup mocks
        mock_user = {"_id": "1", "email": "test@example.com"}
        mock_db.users.find_one.return_value = mock_user
        mock_db.password_resets.insert_one = MagicMock()
        
        result = forgot_password("test@example.com")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertIn("link has been sent", result["message"])
        mock_db.password_resets.insert_one.assert_called_once()
        mock_send_email.assert_called_once()
        
        # Verify inserted token details
        inserted_doc = mock_db.password_resets.insert_one.call_args[0][0]
        self.assertEqual(inserted_doc["email"], "test@example.com")
        self.assertFalse(inserted_doc["is_used"])
        # Check token expiry is set correctly roughly 30 minutes in future
        expires_at = inserted_doc["expires_at"]
        now = datetime.now(timezone.utc)
        self.assertTrue(now < expires_at < now + timedelta(minutes=31))

    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.send_reset_email')
    def test_forgot_password_user_not_exists(self, mock_send_email, mock_db):
        from app.services.auth_service import forgot_password
        
        mock_db.users.find_one.return_value = None
        mock_db.password_resets.insert_one = MagicMock()
        
        # Measure time elapsed to verify dummy bcrypt operations
        start_time = time.time()
        result = forgot_password("nonexistent@example.com")
        duration = time.time() - start_time
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertIn("link has been sent", result["message"])
        mock_db.password_resets.insert_one.assert_not_called()
        mock_send_email.assert_not_called()
        # Verify timing protection was applied (bcrypt rounds=12 takes > 50ms)
        self.assertGreaterEqual(duration, 0.05, "Timing mitigation was too fast, enumeration possible!")

    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.hash_password')
    def test_reset_password_success(self, mock_hash, mock_db):
        from app.services.auth_service import reset_password
        
        # 1. Setup Mock Reset Record
        mock_reset = {
            "_id": "reset_id",
            "email": "test@example.com",
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=30),
            "is_used": False
        }
        mock_db.password_resets.find_one.return_value = mock_reset
        mock_db.users.update_one.return_value = MagicMock(matched_count=1)
        mock_db.password_resets.update_one = MagicMock()
        
        mock_hash.return_value = "mocked_new_hash"
        
        # Call service
        result = reset_password("valid_token", "NewSecure123!")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Password updated successfully")
        
        # Verify user update
        mock_db.users.update_one.assert_called_once_with(
            {"email": "test@example.com"},
            {"$set": {"password_hash": "mocked_new_hash", "updated_at": unittest.mock.ANY}}
        )
        
        # Verify token invalidation
        mock_db.password_resets.update_one.assert_called_once_with(
            {"_id": "reset_id"},
            {"$set": {"is_used": True, "used_at": unittest.mock.ANY}}
        )

    @patch('app.services.auth_service.db')
    def test_reset_password_expired_token(self, mock_db):
        from app.services.auth_service import reset_password
        
        # Setup expired reset record
        mock_reset = {
            "_id": "reset_id",
            "email": "test@example.com",
            "expires_at": datetime.now(timezone.utc) - timedelta(minutes=1), # Expired
            "is_used": False
        }
        mock_db.password_resets.find_one.return_value = mock_reset
        
        result = reset_password("expired_token", "NewSecure123!")
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Invalid or expired token")
        mock_db.users.update_one.assert_not_called()


class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(auth_bp, url_prefix='/api/auth')
        self.client = self.app.test_client()

    @patch('app.routes.auth_routes.forgot_password')
    def test_forgot_password_route(self, mock_forgot_pw):
        mock_forgot_pw.return_value = {
            "success": True,
            "message": "Generic response message"
        }
        
        # Test success case
        response = self.client.post('/api/auth/forgot-password', json={"email": "user@example.com"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Generic response message")
        
        # Test missing email
        response = self.client.post('/api/auth/forgot-password', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("email", data["errors"])

    @patch('app.routes.auth_routes.reset_password')
    def test_reset_password_route(self, mock_reset_pw):
        mock_reset_pw.return_value = {
            "success": True,
            "message": "Password updated successfully"
        }
        
        # Test success
        response = self.client.post('/api/auth/reset-password', json={
            "token": "valid_token",
            "new_password": "NewPassword123!"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        
        # Test validation failure from service
        mock_reset_pw.return_value = {
            "success": False,
            "message": "Invalid or expired token"
        }
        response = self.client.post('/api/auth/reset-password', json={
            "token": "bad_token",
            "new_password": "NewPassword123!"
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Invalid or expired token")

    @patch('app.utils.rate_limiter.db')
    @patch('app.routes.auth_routes.forgot_password')
    def test_forgot_password_rate_limiting(self, mock_forgot_pw, mock_db):
        mock_forgot_pw.return_value = {
            "success": True,
            "message": "Generic success message"
        }
        
        # Simulate 5 requests in last 15 mins
        mock_db.rate_limits.count_documents.return_value = 5
        
        response = self.client.post('/api/auth/forgot-password', json={"email": "test@example.com"})
        
        self.assertEqual(response.status_code, 429)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Rate limit exceeded", data["errors"]["email"])

    @patch('app.routes.auth_routes.reset_password')
    def test_reset_password_error_field_mapping(self, mock_reset_pw):
        # 1. Test token issue mapping
        mock_reset_pw.return_value = {
            "success": False,
            "message": "Invalid or expired token",
            "error_field": "token"
        }
        response = self.client.post('/api/auth/reset-password', json={
            "token": "bad_token",
            "new_password": "NewPassword123!"
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["errors"], {"token": "Invalid or expired token"})
        
        # 2. Test password strength issue mapping
        mock_reset_pw.return_value = {
            "success": False,
            "message": "Password must contain at least one letter",
            "error_field": "new_password"
        }
        response = self.client.post('/api/auth/reset-password', json={
            "token": "valid_token",
            "new_password": "12345678"
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["errors"], {"new_password": "Password must contain at least one letter"})

if __name__ == '__main__':
    unittest.main()
