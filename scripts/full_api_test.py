"""
scripts/full_api_test.py
End-to-end functional test of all product API endpoints.
Run: py scripts/full_api_test.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import json  # noqa: E402
from app import create_app  # noqa: E402

app = create_app()
client = app.test_client()

PASS = []
FAIL = []

def check(label, resp, expected_status):
    data = resp.get_json()
    ok = resp.status_code == expected_status
    tag = "[PASS]" if ok else "[FAIL]"
    print(f"{tag} {label} => HTTP {resp.status_code} (expected {expected_status})")
    if not ok:
        print(f"       Response: {json.dumps(data, indent=2)[:300]}")
        FAIL.append(label)
    else:
        PASS.append(label)
    return data

with app.test_request_context():
    pass

print("\n=== 1. LIST products (empty DB) ===")
r = client.get("/api/products")
check("GET /api/products", r, 200)

print("\n=== 2. SEARCH (short query - expect 400) ===")
r = client.get("/api/products/search?q=a")
check("GET /api/products/search?q=a (too short)", r, 400)

print("\n=== 3. CREATE product (missing fields - expect 400) ===")
r = client.post("/api/products", json={})
check("POST /api/products (empty body)", r, 400)

print("\n=== 4. CREATE product (invalid type - expect 400) ===")
r = client.post("/api/products", json={
    "category_id": "000000000000000000000001",
    "title": "Test Sign",
    "slug": "test-sign",
    "type": "invalid_type",
    "base_price": 99.99,
})
check("POST /api/products (invalid type)", r, 400)

print("\n=== 5. CREATE product (negative price - expect 400) ===")
r = client.post("/api/products", json={
    "category_id": "000000000000000000000001",
    "title": "Test Sign",
    "type": "pre_designed",
    "base_price": -10,
})
check("POST /api/products (negative price)", r, 400)

print("\n=== 6. CREATE product (valid - expect 201) ===")
r = client.post("/api/products", json={
    "category_id": "000000000000000000000001",
    "category_slug": "neon-signs",
    "title": "Galaxy Neon Sign",
    "type": "pre_designed",
    "base_price": 149.99,
    "stock_status": "in_stock",
    "tags": ["neon", "galaxy", "sign", "customtag"],
    "description": "A stunning galaxy themed neon sign.",
    "is_featured": True,
})
d = check("POST /api/products (valid)", r, 201)
created_slug = d.get("data", {}).get("slug") if d else None
print(f"       Created slug: {created_slug}")

if created_slug:
    print("\n=== 7. GET product by slug ===")
    r = client.get(f"/api/products/{created_slug}")
    check(f"GET /api/products/{created_slug}", r, 200)

    print("\n=== 8. LIST products (should have 1) ===")
    r = client.get("/api/products")
    d = check("GET /api/products (after create)", r, 200)
    count = len(d.get("data", [])) if d else 0
    print(f"       Products returned: {count}")

    print("\n=== 9. SEARCH products ===")
    r = client.get("/api/products/search?q=galaxy")
    d = check("GET /api/products/search?q=galaxy", r, 200)

    print("\n=== 9b. SEARCH products by tag ===")
    r = client.get("/api/products/search?q=customtag")
    d = check("GET /api/products/search?q=customtag", r, 200)
    products = d.get("data", []) if d else []
    assert len(products) > 0, "Expected to find at least one product with tag 'customtag'"
    assert products[0]["slug"] == created_slug, f"Expected product slug to be {created_slug}, but got {products[0]['slug'] if products else None}"
    print("       Tag search verified successfully!")

    print("\n=== 10. FILTER by category ===")
    r = client.get("/api/products?category=neon-signs")
    check("GET /api/products?category=neon-signs", r, 200)

    print("\n=== 11. FILTER by price range ===")
    r = client.get("/api/products?min_price=100&max_price=200")
    check("GET /api/products?min_price=100&max_price=200", r, 200)

    print("\n=== 12. FILTER featured ===")
    r = client.get("/api/products?featured=true")
    check("GET /api/products?featured=true", r, 200)

    print("\n=== 13. SORT options ===")
    for sort in ["newest", "price_asc", "price_desc", "popular"]:
        r = client.get(f"/api/products?sort={sort}")
        check(f"GET /api/products?sort={sort}", r, 200)

    print("\n=== 14. UPDATE product ===")
    r = client.put(f"/api/products/{created_slug}", json={"base_price": 199.99, "is_featured": False})
    check(f"PUT /api/products/{created_slug}", r, 200)

    print("\n=== 15. GET non-existent product (expect 404) ===")
    r = client.get("/api/products/does-not-exist")
    check("GET /api/products/does-not-exist", r, 404)

    print("\n=== 16. DELETE product ===")
    r = client.delete(f"/api/products/{created_slug}")
    check(f"DELETE /api/products/{created_slug}", r, 200)

    print("\n=== 17. GET deleted product (expect 404) ===")
    r = client.get(f"/api/products/{created_slug}")
    check(f"GET /api/products/{created_slug} (after delete)", r, 404)

    print("\n=== 18. DELETE same product again (expect 404) ===")
    r = client.delete(f"/api/products/{created_slug}")
    check(f"DELETE /api/products/{created_slug} (again)", r, 404)

print("\n=== 19. HEALTH endpoint ===")
r = client.get("/api/health")
check("GET /api/health", r, 200)

print(f"\n{'='*50}")
print(f"Results: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print(f"FAILED tests: {FAIL}")
    sys.exit(1)
else:
    print("All tests passed!")
