import os
import sys
import pytest
from datetime import datetime, timezone

# Ensure we use mock DB during tests
os.environ["MONGO_URI"] = "mock"
os.environ["MONGO_DB_NAME"] = "galxy_test"

# Add root folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ----------------------------------------------------
# Dynamic Mocking of app.middleware.auth for testing
# ----------------------------------------------------
from unittest.mock import MagicMock
from app.utils._dev_auth_stub import require_admin, generate_admin_token

mock_auth = MagicMock()
mock_auth.require_admin = require_admin
mock_auth.generate_admin_token = generate_admin_token
sys.modules['app.middleware'] = MagicMock()
sys.modules['app.middleware.auth'] = mock_auth

from app import create_app
from app.db import Database
from app.utils.content_schema_validator import validate_content, is_valid_url
from app.middleware.auth import generate_admin_token

@pytest.fixture
def app():
    from tests.conftest import TestConfig
    from app.db import Database
    Database._client = None
    Database._db = None
    # Initialize the app factory with TestConfig to use mock DB
    app = create_app(TestConfig)
    # Ensure indexes are run on startup
    Database.init_db()
    yield app
    # Clear collection after test
    db = Database.get_db()
    db['site_content'].delete_many({})

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_token():
    return generate_admin_token(user_id="admin_1", role="admin")

@pytest.fixture
def user_token():
    return generate_admin_token(user_id="user_1", role="user")


# ==========================================
# 1. Content Schema Validator Tests
# ==========================================

def test_url_validation():
    assert is_valid_url("https://res.cloudinary.com/test.jpg") is True
    assert is_valid_url("http://res.cloudinary.com/test.mp4") is True
    assert is_valid_url("/shop") is True
    assert is_valid_url("/products/lighting") is True
    assert is_valid_url("res.cloudinary.com/test.jpg") is False
    assert is_valid_url("ftp://res.cloudinary.com/test.jpg") is False
    assert is_valid_url(None) is False
    assert is_valid_url(123) is False

def test_validator_url_relative_path_rules():
    # 1. cta_link in hero allows root-relative path
    hero_content = {
        "headline": "Welcome",
        "subheadline": "Studio description",
        "background_video_url": "https://res.cloudinary.com/video.mp4",
        "background_image_url": "https://res.cloudinary.com/image.jpg",
        "cta_text": "Click here",
        "cta_link": "/shop"
    }
    is_valid, errors = validate_content("hero", hero_content)
    assert is_valid is True

    # 2. background_image_url in hero does NOT allow root-relative path
    hero_content_invalid = {
        "headline": "Welcome",
        "subheadline": "Studio description",
        "background_video_url": "https://res.cloudinary.com/video.mp4",
        "background_image_url": "/workshop_image.jpg",
        "cta_text": "Click here",
        "cta_link": "https://res.cloudinary.com/link"
    }
    is_valid_inv, errors_inv = validate_content("hero", hero_content_invalid)
    assert is_valid_inv is False
    assert "background_image_url" in errors_inv

    # 3. social_links.instagram does NOT allow root-relative path
    social_content = {
        "instagram": "/just-a-path",
        "facebook": "https://facebook.com/galxystudio",
        "youtube": "https://youtube.com/c/galxystudio"
    }
    is_valid_soc, errors_soc = validate_content("social_links", social_content)
    assert is_valid_soc is False
    assert "instagram" in errors_soc

def test_validator_valid_hero():
    hero_content = {
        "headline": "Welcome",
        "subheadline": "Studio description",
        "background_video_url": "https://res.cloudinary.com/video.mp4",
        "background_image_url": "https://res.cloudinary.com/image.jpg",
        "cta_text": "Click here",
        "cta_link": "https://res.cloudinary.com/link"
    }
    is_valid, errors = validate_content("hero", hero_content)
    assert is_valid is True
    assert len(errors) == 0

def test_validator_invalid_hero_missing_fields():
    # Missing headline and background_image_url
    hero_content = {
        "subheadline": "Studio description",
        "cta_text": "Click here",
        "cta_link": "https://res.cloudinary.com/link"
    }
    is_valid, errors = validate_content("hero", hero_content)
    assert is_valid is False
    assert "headline" in errors
    assert "background_image_url" in errors

def test_validator_about_body_text_length():
    valid_content = {
        "title": "About",
        "body_text": "a" * 5000,
        "images": ["https://res.cloudinary.com/image1.jpg"],
        "founder_name": "Divakaran",
        "founder_photo": None
    }
    is_valid, errors = validate_content("about", valid_content)
    assert is_valid is True

    invalid_content = {
        "title": "About",
        "body_text": "a" * 5001,
        "images": ["https://res.cloudinary.com/image1.jpg"],
        "founder_name": "Divakaran",
        "founder_photo": None
    }
    is_valid, errors = validate_content("about", invalid_content)
    assert is_valid is False
    assert "body_text" in errors

def test_validator_contact_formats():
    # Invalid email and phone format
    contact_content = {
        "phone": "invalid-phone",
        "whatsapp_number": "+91 99999-88888",  # Should be valid
        "email": "invalid-email-format",
        "address": "123 Street",
        "map_embed_url": "https://res.cloudinary.com/map"
    }
    is_valid, errors = validate_content("contact", contact_content)
    assert is_valid is False
    assert "phone" in errors
    assert "email" in errors
    assert "whatsapp_number" not in errors

def test_validator_footer_quick_links():
    footer_content = {
        "tagline": "Footer",
        "quick_links": [
            {"label": "Home", "url": "https://res.cloudinary.com/home"},
            {"label": "Gallery", "url": "invalid-url"}
        ],
        "business_hours": "9-5"
    }
    is_valid, errors = validate_content("footer", footer_content)
    assert is_valid is False
    assert "quick_links[1].url" in errors


# ==========================================
# 2. Public API Route Tests
# ==========================================

def test_get_section_not_seeded(client):
    response = client.get('/api/site-content/hero')
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "not been seeded" in data["message"]

def test_get_section_invalid_name(client):
    response = client.get('/api/site-content/invalid_sec')
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "Unknown section" in data["message"]

def test_get_section_success(client):
    # Manually seed a section
    db = Database.get_db()
    db['site_content'].insert_one({
        "section": "hero",
        "content": {
            "headline": "Welcome",
            "subheadline": "Sub",
            "background_video_url": None,
            "background_image_url": "https://res.cloudinary.com/image.jpg",
            "cta_text": "Shop",
            "cta_link": "https://res.cloudinary.com/shop"
        },
        "updated_by": "seed",
        "updated_at": datetime.now(timezone.utc)
    })
    
    response = client.get('/api/site-content/hero')
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["section"] == "hero"
    assert data["data"]["content"]["headline"] == "Welcome"

def test_get_bulk_success(client):
    db = Database.get_db()
    # Insert hero
    db['site_content'].insert_one({
        "section": "hero",
        "content": {"headline": "H"},
        "updated_at": datetime.now(timezone.utc),
        "updated_by": "seed"
    })
    # Insert footer
    db['site_content'].insert_one({
        "section": "footer",
        "content": {"tagline": "F"},
        "updated_at": datetime.now(timezone.utc),
        "updated_by": "seed"
    })
    
    # 1. Test clean valid bulk GET
    response = client.get('/api/site-content?sections=hero,footer')
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "hero" in data["data"]
    assert "footer" in data["data"]
    assert data["data"]["hero"]["headline"] == "H"
    assert data["data"]["footer"]["tagline"] == "F"

    # 2. Test mixed valid + invalid bulk GET (F3: must silently drop invalid and return 200)
    response_mixed = client.get('/api/site-content?sections=hero,bogus_sec')
    assert response_mixed.status_code == 200
    data_mixed = response_mixed.get_json()
    assert data_mixed["success"] is True
    assert "hero" in data_mixed["data"]
    assert "bogus_sec" not in data_mixed["data"]
    assert data_mixed["data"]["hero"]["headline"] == "H"


# ==========================================
# 3. Admin API Route & Auth Tests
# ==========================================

def test_admin_routes_auth_failures(client):
    # 1. No header token
    res = client.get('/api/admin/site-content/hero')
    assert res.status_code == 401
    
    # 2. Non-admin role token
    user_tok = generate_admin_token(user_id="user_1", role="user")
    headers = {"Authorization": f"Bearer {user_tok}"}
    res = client.get('/api/admin/site-content/hero', headers=headers)
    assert res.status_code == 403
    
    # 3. Expired/Invalid Token
    headers_invalid = {"Authorization": "Bearer invalid_jwt_token_format"}
    res = client.get('/api/admin/site-content/hero', headers=headers_invalid)
    assert res.status_code == 401

def test_admin_put_success(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "content": {
            "headline": "New Admin Headline",
            "subheadline": "Updated sub",
            "background_video_url": None,
            "background_image_url": "https://res.cloudinary.com/image.jpg",
            "cta_text": "Updated Shop",
            "cta_link": "https://res.cloudinary.com/shop"
        }
    }
    
    response = client.put('/api/admin/site-content/hero', headers=headers, json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["message"] == "Content updated"
    assert data["data"]["content"]["headline"] == "New Admin Headline"
    
    # Verify in DB
    db = Database.get_db()
    stored = db['site_content'].find_one({"section": "hero"})
    assert stored is not None
    assert stored["content"]["headline"] == "New Admin Headline"
    assert stored["updated_by"] == "admin_1"

def test_admin_put_invalid_schema(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "content": {
            "headline": "Missing CTA and other fields"
        }
    }
    response = client.put('/api/admin/site-content/hero', headers=headers, json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "errors" in data
    assert "background_image_url" in data["errors"]

def test_cors_default_config_disallowed(client):
    headers = {"Origin": "http://evil-site.com"}
    response = client.get('/api/site-content/hero', headers=headers)
    assert 'Access-Control-Allow-Origin' not in response.headers

def test_cors_allow_list(client, app):
    app.config['CORS_ALLOWED_ORIGINS'] = 'https://galxystudio.com, https://admin.galxystudio.com'
    
    # Matching origin
    headers_match = {"Origin": "https://galxystudio.com"}
    response = client.get('/api/site-content/hero', headers=headers_match)
    assert response.headers.get('Access-Control-Allow-Origin') == 'https://galxystudio.com'
    assert response.headers.get('Vary') == 'Origin'

    # Disallowed origin
    headers_disallowed = {"Origin": "http://evil-site.com"}
    response = client.get('/api/site-content/hero', headers=headers_disallowed)
    assert 'Access-Control-Allow-Origin' not in response.headers

    # Explicit wildcard config
    app.config['CORS_ALLOWED_ORIGINS'] = '*'
    headers_wildcard = {"Origin": "http://evil-site.com"}
    response_wc = client.get('/api/site-content/hero', headers=headers_wildcard)
    assert response_wc.headers.get('Access-Control-Allow-Origin') == '*'
