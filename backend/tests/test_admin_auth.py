import unittest
import mongomock
from bson import ObjectId
import time
import datetime
import json

from app import create_app
import app.db
from app.utils.password_helper import hash_password
from app.models.admin_user import AdminUser
from app.services.admin_auth_service import AdminAuthService, AdminAuthServiceError
from app.utils.token_helper import generate_access_token, generate_refresh_token, decode_token

class AdminAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_client = mongomock.MongoClient()
        self.app = create_app({
            'TESTING': True,
            'MONGO_CLIENT': self.mock_client,
            'DATABASE_NAME': 'galxy_test'
        })
        self.client = self.app.test_client()
        self.db = self.mock_client['galxy_test']
        self.db.admin_users.delete_many({})
        self.db.users.delete_many({})

    def test_admin_user_model(self):
        pw_hash = hash_password("AdminPassword123")
        doc = AdminUser.create_document("Admin Asil", "admin@galxy.in", pw_hash)
        self.assertEqual(doc["name"], "Admin Asil")
        self.assertEqual(doc["email"], "admin@galxy.in")
        self.assertEqual(doc["role"], "super_admin")
        self.assertTrue(doc["is_active"])
        
        public = AdminUser.to_public_dict(doc)
        self.assertNotIn("password_hash", public)
        self.assertEqual(public["email"], "admin@galxy.in")

    def test_admin_login_service_success(self):
        pw_hash = hash_password("AdminPassword123")
        admin_doc = AdminUser.create_document("Admin Asil", "admin@galxy.in", pw_hash)
        admin_id = self.db.admin_users.insert_one(admin_doc).inserted_id
        
        admin_data, access_token, refresh_token = AdminAuthService.login("admin@galxy.in", "AdminPassword123")
        self.assertEqual(admin_data["email"], "admin@galxy.in")
        self.assertEqual(admin_data["_id"], str(admin_id))
        
        # Verify access token
        payload = decode_token(access_token)
        self.assertEqual(payload["sub"], str(admin_id))
        self.assertEqual(payload["role"], "super_admin")

    def test_admin_login_service_failures(self):
        pw_hash = hash_password("AdminPassword123")
        admin_doc = AdminUser.create_document("Admin Asil", "admin@galxy.in", pw_hash)
        self.db.admin_users.insert_one(admin_doc)
        
        # Wrong password
        with self.assertRaises(AdminAuthServiceError) as context:
            AdminAuthService.login("admin@galxy.in", "WrongPassword")
        self.assertEqual(context.exception.status_code, 401)
        
        # Non-existent admin
        with self.assertRaises(AdminAuthServiceError) as context:
            AdminAuthService.login("nonexistent@galxy.in", "AdminPassword123")
        self.assertEqual(context.exception.status_code, 401)
        
        # Deactivated admin
        self.db.admin_users.update_one({"email": "admin@galxy.in"}, {"$set": {"is_active": False}})
        with self.assertRaises(AdminAuthServiceError) as context:
            AdminAuthService.login("admin@galxy.in", "AdminPassword123")
        self.assertEqual(context.exception.status_code, 403)

    def test_admin_routes_login_logout_me_refresh(self):
        # Seed admin
        pw_hash = hash_password("AdminPassword123")
        admin_doc = AdminUser.create_document("Admin Asil", "admin@galxy.in", pw_hash)
        self.db.admin_users.insert_one(admin_doc)
        
        # 1. Login Route
        res = self.client.post('/api/admin/auth/login', json={
            "email": "admin@galxy.in",
            "password": "AdminPassword123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["admin"]["email"], "admin@galxy.in")
        access_token = data["data"]["access_token"]
        
        # Check Cookie is set
        cookies = res.headers.getlist('Set-Cookie')
        self.assertTrue(any('admin_refresh_token=' in c for c in cookies))
        
        # Extract cookie value
        cookie_header = [c for c in cookies if 'admin_refresh_token=' in c][0]
        refresh_cookie = cookie_header.split('admin_refresh_token=')[1].split(';')[0]
        
        # 2. Get Me Route (Authorized)
        res_me = self.client.get('/api/admin/auth/me', headers={
            "Authorization": f"Bearer {access_token}"
        })
        self.assertEqual(res_me.status_code, 200)
        self.assertTrue(res_me.get_json()["success"])
        
        # 3. Refresh Route
        # Set cookie on test client
        self.client.set_cookie(key='admin_refresh_token', value=refresh_cookie, path='/api/admin/auth')
        res_refresh = self.client.post('/api/admin/auth/refresh')
        self.assertEqual(res_refresh.status_code, 200)
        refresh_data = res_refresh.get_json()
        self.assertTrue(refresh_data["success"])
        self.assertIsNotNone(refresh_data["data"]["access_token"])
        
        # 4. Logout Route
        res_logout = self.client.post('/api/admin/auth/logout')
        self.assertEqual(res_logout.status_code, 200)
        logout_cookies = res_logout.headers.getlist('Set-Cookie')
        self.assertTrue(any('admin_refresh_token=;' in c or 'Max-Age=0' in c or 'expires=' in c for c in logout_cookies))

    def test_admin_rate_limiter(self):
        # We check that rate limiter blocks logins after 5 attempts
        from app.utils.rate_limiter import RateLimiter
        limiter = RateLimiter(limit=3, window_seconds=2)
        key = "127.0.0.1+admin_test@galxy.in"
        
        self.assertFalse(limiter.is_rate_limited(key))
        self.assertFalse(limiter.is_rate_limited(key))
        self.assertFalse(limiter.is_rate_limited(key))
        self.assertTrue(limiter.is_rate_limited(key))

if __name__ == '__main__':
    unittest.main()
