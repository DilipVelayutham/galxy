import os
import sys
import time
import uuid
import json
import threading

# Set environment variables for testing before imports
os.environ["MOCK_AI"] = "True"
os.environ["TESTING"] = "True"
os.environ["AI_FREE_GENERATIONS_PER_SESSION"] = "5"
os.environ["AI_MAX_GENERATIONS_PER_USER_PER_DAY"] = "20"
os.environ["MONGO_URI"] = "mongodb://localhost:27017/test_db"
os.environ["CLOUDINARY_CLOUD_NAME"] = "mock_cloud"
os.environ["CLOUDINARY_API_KEY"] = "mock_key"
os.environ["CLOUDINARY_API_SECRET"] = "mock_secret"

# Patch pymongo.MongoClient to use mongomock.MongoClient BEFORE importing database module
import mongomock
import pymongo
pymongo.MongoClient = mongomock.MongoClient

# Mock Cloudinary upload & destroy globally for unit tests to prevent external API calls
import cloudinary.uploader
cloudinary.uploader.upload = lambda file, **options: {
    "secure_url": "https://res.cloudinary.com/mock_cloud/image/upload/v1/mock.png",
    "public_id": "galxy/ai-previews/mock_public_id"
}
cloudinary.uploader.destroy = lambda public_id, **options: {"result": "ok"}

# Import create_app and database collections
from app import create_app
from app.database import categories, ai_generations, ai_cache

# Initialize Flask app
app = create_app()

# Seed database with Category for testing
category_id = "test_custom_apparels"
categories.update_one(
    {"category_id": category_id},
    {"$set": {
        "category_id": category_id,
        "slug": "test-custom-apparels",
        "name": "Test Custom Apparels",
        "is_active": True,
        "ai_prompt_template": "A {color} {style} with '{custom_text}' logo.",
        "attribute_schema": [
            {"key": "style", "label": "Style", "type": "select", "required": True, "affects_ai_preview": True, "options": [{"value": "tshirt", "label": "T-Shirt"}]},
            {"key": "color", "label": "Color", "type": "color_swatch", "required": True, "affects_ai_preview": True, "options": [{"value": "black", "label": "Black"}]},
            {"key": "custom_text", "label": "Text", "type": "text_input", "required": True, "affects_ai_preview": True}
        ]
    }},
    upsert=True
)

# Start Flask server in background thread
from werkzeug.serving import make_server
class ServerThread(threading.Thread):
    def __init__(self, app, port=5000):
        super().__init__()
        self.server = make_server('127.0.0.1', port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

print("Starting Flask server on http://127.0.0.1:5000 ...")
server = ServerThread(app, port=5000)
server.start()
time.sleep(1) # wait for server to spin up

import requests

BASE_URL = "http://127.0.0.1:5000"

def log_test_case(name, method, url, headers=None, payload=None):
    print("\n" + "=" * 70)
    print(f"TEST CASE: {name}")
    print("=" * 70)
    print(f"REQUEST:")
    print(f"  Method: {method}")
    print(f"  URL:    {url}")
    if headers:
        print(f"  Headers: {json.dumps(headers, indent=2)}")
    if payload:
        print(f"  Payload: {json.dumps(payload, indent=2)}")
    print("-" * 70)

def log_response(response):
    print(f"RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"  Body: {json.dumps(data, indent=2)}")
    except ValueError:
        print(f"  Body: {response.text}")
    print("=" * 70)

# Clear collection logs for clean test runs
ai_generations.delete_many({})
ai_cache.delete_many({})

try:
    # --------------------------------------------------------------------------
    # 1. GET API Status
    # --------------------------------------------------------------------------
    log_test_case("1. GET API Status", "GET", f"{BASE_URL}/")
    r = requests.get(f"{BASE_URL}/")
    log_response(r)
    assert r.status_code == 200

    # --------------------------------------------------------------------------
    # 2. POST Generate Preview (Success Case)
    # --------------------------------------------------------------------------
    payload_success = {
        "category_id": category_id,
        "selected_attributes": {
            "style": "tshirt",
            "color": "black",
            "custom_text": "LTI Hub"
        },
        "session_id": str(uuid.uuid4())
    }
    log_test_case("2. Generate Preview - Success Case", "POST", f"{BASE_URL}/api/ai/generate-preview", payload=payload_success)
    r = requests.post(f"{BASE_URL}/api/ai/generate-preview", json=payload_success)
    log_response(r)
    assert r.status_code == 200
    assert r.json()["success"] is True

    # --------------------------------------------------------------------------
    # 3. POST Generate Preview (Validation Failure Case)
    # --------------------------------------------------------------------------
    payload_invalid = {
        "category_id": category_id,
        "selected_attributes": {
            "style": "jeans", # Invalid style option
            "color": "black",
            "custom_text": "LTI Hub"
        }
    }
    log_test_case("3. Generate Preview - Validation Failure Case", "POST", f"{BASE_URL}/api/ai/generate-preview", payload=payload_invalid)
    r = requests.post(f"{BASE_URL}/api/ai/generate-preview", json=payload_invalid)
    log_response(r)
    assert r.status_code == 400
    assert r.json()["success"] is False

    # --------------------------------------------------------------------------
    # 4. POST Generate Preview (Caching & Cache Hit Case)
    # --------------------------------------------------------------------------
    # For caching to hit, custom_text should not be present in attributes of the category
    # Let's seed a no-text category to check cache
    temp_cat_id = "cache_test_category"
    categories.update_one(
        {"category_id": temp_cat_id},
        {"$set": {
            "category_id": temp_cat_id,
            "name": "Cache Test Category",
            "ai_prompt_template": "A {color} {style}.",
            "attribute_schema": [
                {"key": "style", "label": "Style", "type": "select", "required": True, "affects_ai_preview": True, "options": [{"value": "tshirt", "label": "T-Shirt"}]},
                {"key": "color", "label": "Color", "type": "color_swatch", "required": True, "affects_ai_preview": True, "options": [{"value": "black", "label": "Black"}]}
            ]
        }},
        upsert=True
    )

    payload_cache = {
        "category_id": temp_cat_id,
        "selected_attributes": {
            "style": "tshirt",
            "color": "black"
        },
        "session_id": str(uuid.uuid4())
    }

    # Query 1: Cache Miss
    log_test_case("4a. Generate Preview - Cache Miss (First Call)", "POST", f"{BASE_URL}/api/ai/generate-preview", payload=payload_cache)
    r1 = requests.post(f"{BASE_URL}/api/ai/generate-preview", json=payload_cache)
    log_response(r1)
    assert r1.status_code == 200
    assert r1.json()["data"]["from_cache"] is False

    # Query 2: Cache Hit
    log_test_case("4b. Generate Preview - Cache Hit (Second Call)", "POST", f"{BASE_URL}/api/ai/generate-preview", payload=payload_cache)
    r2 = requests.post(f"{BASE_URL}/api/ai/generate-preview", json=payload_cache)
    log_response(r2)
    assert r2.status_code == 200
    assert r2.json()["data"]["from_cache"] is True

    # --------------------------------------------------------------------------
    # 5. POST Generate Preview (Session Quota Rate Limiting Case)
    # --------------------------------------------------------------------------
    # Clear logs to reset rate limiting counters for this IP
    ai_generations.delete_many({})
    
    session_id = f"test_session_{uuid.uuid4()}"
    payload_limit = {
        "category_id": category_id,
        "selected_attributes": {
            "style": "tshirt",
            "color": "black",
            "custom_text": "LTI"
        },
        "session_id": session_id
    }
    
    log_test_case("5a. Generate Preview - Hit limit sequentially (Calls 1-5)", "POST", f"{BASE_URL}/api/ai/generate-preview", payload=payload_limit)
    for i in range(5):
        payload_limit["selected_attributes"]["custom_text"] = f"LTI {i}"
        r = requests.post(f"{BASE_URL}/api/ai/generate-preview", json=payload_limit)
        print(f"  Call {i+1}: Status {r.status_code}")
        assert r.status_code == 200
        
    log_test_case("5b. Generate Preview - Call 6 (Expected 429 Rate Limit Exceeded)", "POST", f"{BASE_URL}/api/ai/generate-preview", payload=payload_limit)
    payload_limit["selected_attributes"]["custom_text"] = "LTI Block"
    r = requests.post(f"{BASE_URL}/api/ai/generate-preview", json=payload_limit)
    log_response(r)
    assert r.status_code == 429

    # --------------------------------------------------------------------------
    # 6. GET User history (Authorized Case)
    # --------------------------------------------------------------------------
    ai_generations.delete_many({})
    user_id = "user_12345"
    payload_user = {
        "category_id": category_id,
        "selected_attributes": {
            "style": "tshirt",
            "color": "black",
            "custom_text": "History item"
        },
        "user_id": user_id
    }
    
    # Generate history item
    requests.post(f"{BASE_URL}/api/ai/generate-preview", json=payload_user)
    
    headers_auth = {"X-User-Id": user_id}
    log_test_case("6. GET User History - Authorized Case", "GET", f"{BASE_URL}/api/ai/generations/{user_id}", headers=headers_auth)
    r = requests.get(f"{BASE_URL}/api/ai/generations/{user_id}", headers=headers_auth)
    log_response(r)
    assert r.status_code == 200
    assert r.json()["success"] is True

    # --------------------------------------------------------------------------
    # 7. GET User history (Unauthorized Case)
    # --------------------------------------------------------------------------
    headers_unauth = {"X-User-Id": "wrong_user_id"}
    log_test_case("7. GET User History - Unauthorized Case (Wrong ID)", "GET", f"{BASE_URL}/api/ai/generations/{user_id}", headers=headers_unauth)
    r = requests.get(f"{BASE_URL}/api/ai/generations/{user_id}", headers=headers_unauth)
    log_response(r)
    assert r.status_code == 403
    assert r.json()["success"] is False

    # --------------------------------------------------------------------------
    # 8. GET Admin Analytics (Authorized Case)
    # --------------------------------------------------------------------------
    headers_admin = {"X-User-Role": "admin"}
    log_test_case("8. GET Admin Analytics - Authorized Case", "GET", f"{BASE_URL}/api/admin/ai/generations?limit=2", headers=headers_admin)
    r = requests.get(f"{BASE_URL}/api/admin/ai/generations?limit=2", headers=headers_admin)
    log_response(r)
    assert r.status_code == 200
    assert r.json()["success"] is True

    # --------------------------------------------------------------------------
    # 9. GET Admin Analytics (Unauthorized Case)
    # --------------------------------------------------------------------------
    log_test_case("9. GET Admin Analytics - Unauthorized Case (Non-admin)", "GET", f"{BASE_URL}/api/admin/ai/generations")
    r = requests.get(f"{BASE_URL}/api/admin/ai/generations")
    log_response(r)
    assert r.status_code == 403
    assert r.json()["success"] is False

    print("\n" + "=" * 70)
    print("ALL POSTMAN-STYLE HTTP TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

finally:
    # Cleanup temp category
    categories.delete_one({"category_id": temp_cat_id})
    print("Shutting down Flask server...")
    server.shutdown()
    server.join()
    print("Server stopped.")
