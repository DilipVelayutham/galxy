import unittest
import mongomock
from bson import ObjectId
import time
import jwt
import datetime

# Import application components
from app import create_app
import app.db
from app.utils.password_helper import hash_password, verify_password
from app.utils.validators import validate_email, validate_password, validate_phone, validate_pincode
from app.utils.token_helper import generate_access_token, generate_refresh_token, decode_token, ExpiredTokenError, InvalidTokenError
from app.configs.jwt_config import JWTConfig
from app.models.user import User
from app.models.admin_user import AdminUser
from app.services.auth_service import AuthService, AuthServiceError

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        # Create mock mongo client
        self.mock_client = mongomock.MongoClient()
        # Initialize Flask in testing mode
        self.app = create_app({
            'TESTING': True,
            'MONGO_CLIENT': self.mock_client,
            'DATABASE_NAME': 'galxy_test'
        })
        self.client = self.app.test_client()
        
        # Access the mock DB directly to seed/verify data
        self.db = self.mock_client['galxy_test']
        # Clear collections
        self.db.users.delete_many({})
        self.db.admin_users.delete_many({})

    def test_password_helper(self):
        password = "SecurePass123"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPass123", hashed))
        with self.assertRaises(ValueError):
            hash_password("")

    def test_validators(self):
        # Email
        v_ok, email = validate_email("user@example.com")
        self.assertTrue(v_ok)
        self.assertEqual(email, "user@example.com")
        v_ok, _ = validate_email("invalid-email")
        self.assertFalse(v_ok)
        
        # Password
        v_ok, _ = validate_password("Pass1234") # 8 chars, letter + number
        self.assertTrue(v_ok)
        v_ok, err = validate_password("Pass")
        self.assertFalse(v_ok)
        self.assertIn("at least 8 characters", err)
        v_ok, err = validate_password("12345678") # no letter
        self.assertFalse(v_ok)
        v_ok, err = validate_password("abcdefgh") # no number
        self.assertFalse(v_ok)
        
        # Phone
        v_ok, phone = validate_phone("9876543210")
        self.assertTrue(v_ok)
        self.assertEqual(phone, "9876543210")
        v_ok, _ = validate_phone("1234567890") # must start with 6-9
        self.assertFalse(v_ok)
        v_ok, _ = validate_phone("98765432") # must be 10 digits
        self.assertFalse(v_ok)
        
        # Pincode
        v_ok, pincode = validate_pincode("600001")
        self.assertTrue(v_ok)
        self.assertEqual(pincode, "600001")
        v_ok, _ = validate_pincode("60000a")
        self.assertFalse(v_ok)
        v_ok, _ = validate_pincode("6000")
        self.assertFalse(v_ok)

    def test_token_helper(self):
        user_id = ObjectId()
        # Access token
        access_token = generate_access_token(user_id, "customer")
        payload = decode_token(access_token)
        self.assertEqual(payload["sub"], str(user_id))
        self.assertEqual(payload["role"], "customer")
        
        # Refresh token
        refresh_token = generate_refresh_token(user_id, "customer")
        payload_refresh = decode_token(refresh_token)
        self.assertEqual(payload_refresh["sub"], str(user_id))
        self.assertEqual(payload_refresh["role"], "customer")
        
        # Expired token test
        expired_payload = {
            "sub": str(user_id),
            "role": "customer",
            "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=1)
        }
        expired_token = jwt.encode(expired_payload, JWTConfig.JWT_SECRET, algorithm="HS256")
        with self.assertRaises(ExpiredTokenError):
            decode_token(expired_token)
            
        # Invalid token test
        with self.assertRaises(InvalidTokenError):
            decode_token("some.invalid.token")

    def test_signup_and_login_service(self):
        # Signup
        user, access, refresh = AuthService.signup_user(
            name="John Doe",
            email="john@example.com",
            phone="9876543210",
            password="Password1"
        )
        self.assertEqual(user["email"], "john@example.com")
        self.assertEqual(user["name"], "John Doe")
        self.assertNotIn("password_hash", user)
        self.assertIsNotNone(access)
        self.assertIsNotNone(refresh)
        
        # Duplicate signup
        with self.assertRaises(AuthServiceError) as context:
            AuthService.signup_user(
                name="Jane Doe",
                email="john@example.com",
                phone="9876543211",
                password="Password2"
            )
        self.assertEqual(context.exception.status_code, 409)
        self.assertIn("already registered", context.exception.message)
        
        # Login success
        user_login, access_login, refresh_login = AuthService.login_user(
            email="john@example.com",
            password="Password1"
        )
        self.assertEqual(user_login["_id"], user["_id"])
        
        # Login invalid password
        with self.assertRaises(AuthServiceError) as context:
            AuthService.login_user(
                email="john@example.com",
                password="WrongPassword"
            )
        self.assertEqual(context.exception.status_code, 401)
        
        # Login deactivated user
        self.db.users.update_one({"email": "john@example.com"}, {"$set": {"is_active": False}})
        with self.assertRaises(AuthServiceError) as context:
            AuthService.login_user(
                email="john@example.com",
                password="Password1"
            )
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("deactivated", context.exception.message)

    def test_token_refresh_service(self):
        # Setup active user
        user, access, refresh = AuthService.signup_user(
            name="Test User",
            email="test@example.com",
            phone="9876543212",
            password="Password1"
        )
        
        # Refresh tokens
        new_access, new_refresh = AuthService.refresh_tokens(refresh)
        self.assertIsNotNone(new_access)
        self.assertIsNotNone(new_refresh)
        
        # Ensure new access token decodes correctly
        payload = decode_token(new_access)
        self.assertEqual(payload["sub"], user["_id"])
        
        # Check invalid refresh token
        with self.assertRaises(AuthServiceError) as context:
            AuthService.refresh_tokens("invalid.token")
        self.assertEqual(context.exception.status_code, 401)

    def test_routes_signup_login_logout(self):
        # Test HTTP Signup
        signup_data = {
            "name": "HTTP User",
            "email": "http@example.com",
            "phone": "9876543213",
            "password": "Password1"
        }
        res = self.client.post('/api/auth/signup', json=signup_data)
        self.assertEqual(res.status_code, 201)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["data"]["user"]["email"], "http@example.com")
        self.assertIn("access_token", json_data["data"])
        
        # Verify HTTP Cookie is set
        cookies = res.headers.getlist('Set-Cookie')
        self.assertTrue(any('refresh_token=' in c for c in cookies))
        self.assertTrue(any('HttpOnly' in c for c in cookies))
        
        # Test HTTP Login
        login_data = {
            "email": "http@example.com",
            "password": "Password1"
        }
        res_login = self.client.post('/api/auth/login', json=login_data)
        self.assertEqual(res_login.status_code, 200)
        
        # Test HTTP Logout
        res_logout = self.client.post('/api/auth/logout')
        self.assertEqual(res_logout.status_code, 200)
        logout_cookies = res_logout.headers.getlist('Set-Cookie')
        # Check if cookie is cleared (expiry set in past)
        self.assertTrue(any('refresh_token=;' in c or 'Max-Age=0' in c or 'expires=' in c for c in logout_cookies))

    def test_middleware_role_isolation(self):
        # 1. Create a customer user
        customer_pass_hash = hash_password("Password1")
        customer_doc = User.create_document("Customer", "cust@example.com", "9876543214", customer_pass_hash)
        cust_id = self.db.users.insert_one(customer_doc).inserted_id
        customer_token = generate_access_token(cust_id, "customer")
        
        # 2. Create an admin user
        admin_pass_hash = hash_password("AdminPassword1")
        admin_doc = AdminUser.create_document("Admin Asil", "asil@example.com", admin_pass_hash)
        admin_id = self.db.admin_users.insert_one(admin_doc).inserted_id
        admin_token = generate_access_token(admin_id, "super_admin")

        # 3. Test @require_auth endpoint (customer profile) with customer token -> Should succeed (200)
        res_profile_ok = self.client.get(
            '/api/user/profile',
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        self.assertEqual(res_profile_ok.status_code, 200)
        
        # 4. Test @require_auth endpoint (customer profile) with admin token -> Should be rejected (403)
        res_profile_admin = self.client.get(
            '/api/user/profile',
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(res_profile_admin.status_code, 403)
        self.assertIn("Customers only", res_profile_admin.get_json()["message"])
        
        # 5. Test @require_admin endpoint (/api/admin/auth/me) with admin token -> Should succeed (200)
        res_me_ok = self.client.get(
            '/api/admin/auth/me',
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(res_me_ok.status_code, 200)
        self.assertEqual(res_me_ok.get_json()["data"]["admin"]["email"], "asil@example.com")
        
        # 6. Test @require_admin endpoint (/api/admin/auth/me) with customer token -> Should be rejected (403)
        res_me_cust = self.client.get(
            '/api/admin/auth/me',
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        self.assertEqual(res_me_cust.status_code, 403)
        self.assertIn("Admins only", res_me_cust.get_json()["message"])

    def test_admin_login_and_refresh_http(self):
        # Seed admin
        admin_pass_hash = hash_password("AdminSecurePass1")
        admin_doc = AdminUser.create_document("Admin Asil", "asil_test@example.com", admin_pass_hash)
        self.db.admin_users.insert_one(admin_doc)
        
        # Test HTTP Admin Login
        login_data = {
            "email": "asil_test@example.com",
            "password": "AdminSecurePass1"
        }
        res = self.client.post('/api/admin/auth/login', json=login_data)
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["data"]["admin"]["email"], "asil_test@example.com")
        self.assertIn("access_token", json_data["data"])
        
        # Verify access token payload type and role
        payload = decode_token(json_data["data"]["access_token"])
        self.assertEqual(payload["type"], "access")
        self.assertEqual(payload["role"], "super_admin")
        
        # Verify admin_refresh_token Cookie is set
        cookies = res.headers.getlist('Set-Cookie')
        self.assertTrue(any('admin_refresh_token=' in c for c in cookies))
        
        # Extract refresh token from cookie
        import re
        cookie_header = res.headers.get('Set-Cookie')
        match = re.search(r'admin_refresh_token=([^;]+)', cookie_header)
        refresh_token = match.group(1) if match else None
        self.assertIsNotNone(refresh_token)
        
        # Decode and verify refresh token payload
        payload_refresh = decode_token(refresh_token)
        self.assertEqual(payload_refresh["type"], "refresh")
        self.assertEqual(payload_refresh["role"], "super_admin")
        
        # Test HTTP Admin Refresh
        self.client.set_cookie('admin_refresh_token', refresh_token, path='/api/admin/auth')
        res_refresh = self.client.post('/api/admin/auth/refresh')
        self.assertEqual(res_refresh.status_code, 200)
        json_refresh = res_refresh.get_json()
        self.assertTrue(json_refresh["success"])
        self.assertIn("access_token", json_refresh["data"])
        
        # Verify rotated cookie is set
        refresh_cookies = res_refresh.headers.getlist('Set-Cookie')
        self.assertTrue(any('admin_refresh_token=' in c for c in refresh_cookies))

    def test_token_type_mismatch_refresh(self):
        # 1. Generate access token for customer
        user_id = ObjectId()
        access_token = generate_access_token(user_id, "customer")
        
        # Try to refresh using customer access token as refresh token cookie
        self.client.set_cookie('refresh_token', access_token, path='/api/auth')
        res = self.client.post('/api/auth/refresh')
        self.assertEqual(res.status_code, 401)
        json_data = res.get_json()
        self.assertFalse(json_data["success"])
        self.assertIn("Invalid token type", json_data["message"])
        self.assertIn("errors", json_data)
        
        # 2. Try to refresh using admin access token as admin refresh token cookie
        admin_id = ObjectId()
        admin_access_token = generate_access_token(admin_id, "super_admin")
        
        self.client.set_cookie('admin_refresh_token', admin_access_token, path='/api/admin/auth')
        res_admin = self.client.post('/api/admin/auth/refresh')
        self.assertEqual(res_admin.status_code, 401)
        json_admin_data = res_admin.get_json()
        self.assertFalse(json_admin_data["success"])
        self.assertIn("Invalid token type", json_admin_data["message"])
        self.assertIn("errors", json_admin_data)

    def test_rate_limiter(self):
        from app.utils.rate_limiter import RateLimiter
        # Create a fresh limiter with low limit for easy testing
        limiter = RateLimiter(limit=3, window_seconds=2)
        key = "127.0.0.1+test_limiter@example.com"
        
        self.assertFalse(limiter.is_rate_limited(key))
        self.assertFalse(limiter.is_rate_limited(key))
        self.assertFalse(limiter.is_rate_limited(key))
        # 4th time should be rate limited
        self.assertTrue(limiter.is_rate_limited(key))
        
        # Wait for window to expire
        time.sleep(2.1)
        # Should be allowed again
        self.assertFalse(limiter.is_rate_limited(key))

if __name__ == '__main__':
    unittest.main()
