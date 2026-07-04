import requests
import json
import time
import uuid

url_prefix = "http://localhost:5000"
test_session_id = f"guest-session-{uuid.uuid4().hex[:8]}"

def test_preview_generation():
    print("--- 1. Testing Fresh AI Preview Generation ---")
    payload = {
        "category_id": "60b9f15f9b1d8b2e8a7f4c01", # Neon Sign
        "session_id": test_session_id,
        "selected_attributes": {
            "color": "pink",
            "font": "cursive",
            "chain": "yes",
            "custom_text": "Antigravity Neon",
            "sku_code": "sku_neon_01"
        },
        "user_id": "60b9f15f9b1d8b2e8a7f4c99" # Logged-in user
    }
    
    start_time = time.time()
    response = requests.post(f"{url_prefix}/api/ai/generate-preview", json=payload)
    elapsed = time.time() - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"Time Taken: {elapsed:.2f}s\n")
    
    # Check if successful
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["from_cache"] is False
    output_url = res_data["data"]["output_image_url"]
    
    print("--- 2. Testing Cache Hit on Identical Configuration ---")
    # Send the exact same request
    start_time = time.time()
    response2 = requests.post(f"{url_prefix}/api/ai/generate-preview", json=payload)
    elapsed2 = time.time() - start_time
    
    print(f"Status Code: {response2.status_code}")
    print(f"Response: {response2.json()}")
    print(f"Time Taken: {elapsed2:.4f}s (should be near instant)\n")
    
    assert response2.status_code == 200
    res_data2 = response2.json()
    assert res_data2["success"] is True
    # Wait, custom_text is present in selected_attributes, so does it cache?
    # Ah! "custom_text" is in selected_attributes, so it should bypass caching!
    # Let's verify that from_cache is False because of custom_text bypass!
    print(f"Bypass verification: from_cache is {res_data2['data']['from_cache']} (should be False due to custom_text bypass)")
    assert res_data2["data"]["from_cache"] is False
 
    print("--- 3. Testing Caching with No custom_text ---")
    # Configuration without custom_text (should be cached)
    payload_no_text = {
        "category_id": "60b9f15f9b1d8b2e8a7f4c01",
        "session_id": test_session_id,
        "selected_attributes": {
            "color": "blue",
            "font": "bold",
            "chain": "no",
            "sku_code": "sku_neon_01"
        }
    }
    
    # Run 1: Fresh run
    requests.post(f"{url_prefix}/api/ai/generate-preview", json=payload_no_text)
    
    # Run 2: Cache Hit
    start_time = time.time()
    response_cache = requests.post(f"{url_prefix}/api/ai/generate-preview", json=payload_no_text)
    elapsed_cache = time.time() - start_time
    
    print(f"Status Code: {response_cache.status_code}")
    print(f"Response: {response_cache.json()}")
    print(f"Time Taken: {elapsed_cache:.4f}s (should be near instant)\n")
    
    assert response_cache.status_code == 200
    assert response_cache.json()["data"]["from_cache"] is True

    print("--- 4. Testing User Generation History ---")
    headers = {
        "X-User-Id": "60b9f15f9b1d8b2e8a7f4c99",
        "X-User-Role": "user"
    }
    response_history = requests.get(f"{url_prefix}/api/ai/generations/60b9f15f9b1d8b2e8a7f4c99", headers=headers)
    print(f"Status Code: {response_history.status_code}")
    print(f"History count: {len(response_history.json().get('data', []))}")
    print(f"History: {response_history.json()}\n")
    
    assert response_history.status_code == 200

    print("--- 5. Testing Admin Full History with Filters ---")
    admin_headers = {
        "X-Admin-Role": "admin"
    }
    response_admin = requests.get(f"{url_prefix}/api/admin/ai/generations?status=success", headers=admin_headers)
    print(f"Status Code: {response_admin.status_code}")
    print(f"Admin History Count: {len(response_admin.json().get('data', []))}")
    print(f"Admin History: {response_admin.json()}\n")
    
    assert response_admin.status_code == 200
    
    print("All integration endpoints verified successfully!")

if __name__ == "__main__":
    time.sleep(2) # Wait for server to boot up
    test_preview_generation()
