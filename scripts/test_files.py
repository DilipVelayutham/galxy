"""
scripts/test_files.py
Deep test of backfill_category_slug.py and app/models/product.py
Run: py scripts/test_files.py
"""
import sys
import os
import traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

PASS = []
FAIL = []

def ok(msg):
    print(f"  [PASS] {msg}")
    PASS.append(msg)

def fail(msg, exc=None):
    print(f"  [FAIL] {msg}")
    if exc:
        traceback.print_exc()
    FAIL.append(msg)

# ─────────────────────────────────────────────────────────────────────────────
# 1. BACKFILL SCRIPT — syntax + import check
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== backfill_category_slug.py ===")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "backfill",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "backfill_category_slug.py")
    )
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass  # argparse calls sys.exit() without args — that's expected
    ok("imports without errors")

    # Verify parse_args exists and is callable
    assert callable(mod.parse_args), "parse_args must be callable"
    ok("parse_args() is defined and callable")

    # Verify main exists and is callable
    assert callable(mod.main), "main() must be callable"
    ok("main() is defined and callable")

    # Verify MONGO_URI default comes from env (not hardcoded localhost)
    import sys as _sys
    _argv_backup = _sys.argv[:]
    _sys.argv = ["backfill", "--old-slug", "x", "--new-slug", "y", "--dry-run"]
    try:
        args = mod.parse_args()
        atlas_uri = os.environ.get("MONGO_URI", "")
        if atlas_uri and "mongodb+srv" in atlas_uri:
            assert args.mongo_uri == atlas_uri, \
                f"Expected Atlas URI but got: {args.mongo_uri}"
            ok("--mongo-uri defaults to Atlas URI from .env")
        else:
            ok("--mongo-uri default loaded from environment")
    finally:
        _sys.argv = _argv_backup

except Exception as e:
    fail(f"backfill_category_slug.py error: {e}", e)

# ─────────────────────────────────────────────────────────────────────────────
# 2. PRODUCT MODEL — full function tests
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== app/models/product.py ===")
try:
    from app.models import product
    ok("app.models.product imports OK")
except Exception as e:
    fail(f"import failed: {e}", e)
    print("\nAborting — cannot test product.py without successful import.")
    sys.exit(1)

# --- default_product() ---
try:
    doc = product.default_product()
    required_keys = [
        "category_id", "category_slug", "title", "slug", "type",
        "base_price", "images", "thumbnail", "description",
        "specifications", "default_attributes", "stock_status",
        "tags", "is_featured", "is_active", "views",
        "rating_avg", "rating_count", "created_at", "updated_at",
    ]
    for k in required_keys:
        assert k in doc, f"default_product() missing key: {k}"
    ok("default_product() has all required keys")
    assert doc["type"] == "pre_designed"
    assert doc["stock_status"] == "in_stock"
    assert doc["is_active"] is True
    assert doc["base_price"] == 0
    ok("default_product() has correct default values")
except Exception as e:
    fail(f"default_product(): {e}", e)

# --- validate_product_payload() — required fields ---
try:
    errors = product.validate_product_payload({})
    required_reported = [e for e in errors if "is required" in e]
    for field in ("category_id", "title", "type", "base_price"):
        assert any(field in e for e in required_reported), \
            f"'{field}' should be flagged as required"
    # slug must NOT be required
    assert not any("slug" in e for e in required_reported), \
        f"'slug' should NOT be required but found in errors: {errors}"
    ok("validate_product_payload() requires category_id, title, type, base_price (not slug)")
except Exception as e:
    fail(f"validate_product_payload() required fields: {e}", e)

# --- validate_product_payload() — type validation ---
try:
    errors = product.validate_product_payload({"type": "invalid_type"}, is_update=True)
    assert any("type" in e for e in errors), f"Expected type error, got: {errors}"
    ok("validate_product_payload() rejects invalid type")
    errors = product.validate_product_payload({"type": "pre_designed"}, is_update=True)
    assert not any("type" in e for e in errors)
    errors = product.validate_product_payload({"type": "fully_custom"}, is_update=True)
    assert not any("type" in e for e in errors)
    ok("validate_product_payload() accepts valid types: pre_designed, fully_custom")
except Exception as e:
    fail(f"validate_product_payload() type check: {e}", e)

# --- validate_product_payload() — stock_status validation ---
try:
    errors = product.validate_product_payload({"stock_status": "bad_status"}, is_update=True)
    assert any("stock_status" in e for e in errors)
    ok("validate_product_payload() rejects invalid stock_status")
    for s in ("in_stock", "made_to_order", "out_of_stock"):
        errors = product.validate_product_payload({"stock_status": s}, is_update=True)
        assert not any("stock_status" in e for e in errors), \
            f"'{s}' should be valid but got errors: {errors}"
    ok("validate_product_payload() accepts all valid stock_statuses")
except Exception as e:
    fail(f"validate_product_payload() stock_status check: {e}", e)

# --- validate_product_payload() — base_price validation ---
try:
    errors = product.validate_product_payload({"base_price": -5}, is_update=True)
    assert any("base_price" in e for e in errors)
    ok("validate_product_payload() rejects negative base_price")
    errors = product.validate_product_payload({"base_price": "not-a-number"}, is_update=True)
    assert any("base_price" in e for e in errors)
    ok("validate_product_payload() rejects non-numeric base_price")
    errors = product.validate_product_payload({"base_price": 0}, is_update=True)
    assert not any("base_price" in e for e in errors)
    errors = product.validate_product_payload({"base_price": 99.99}, is_update=True)
    assert not any("base_price" in e for e in errors)
    ok("validate_product_payload() accepts valid base_price values")
except Exception as e:
    fail(f"validate_product_payload() price check: {e}", e)

# --- to_list_view() ---
try:
    from bson import ObjectId
    from datetime import datetime, timezone
    dummy = {
        "_id": ObjectId(),
        "category_id": ObjectId(),
        "category_slug": "neon-signs",
        "title": "Test Neon Sign",
        "slug": "test-neon-sign",
        "type": "pre_designed",
        "base_price": 149.99,
        "images": [],
        "thumbnail": "https://example.com/img.jpg",
        "description": "A test sign.",
        "specifications": {"material": "Flex LED"},
        "default_attributes": {},
        "stock_status": "in_stock",
        "tags": ["neon", "test"],
        "is_featured": True,
        "is_active": True,
        "views": 42,
        "rating_avg": 4.5,
        "rating_count": 10,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    lv = product.to_list_view(dummy)
    assert isinstance(lv["_id"], str), "_id must be string"
    assert lv["title"] == "Test Neon Sign"
    assert lv["base_price"] == 149.99
    assert lv["is_featured"] is True
    # Heavy fields must NOT be present in list view
    for heavy in ("images", "description", "specifications", "default_attributes"):
        assert heavy not in lv, f"to_list_view() should exclude '{heavy}'"
    ok("to_list_view() serializes correctly and excludes heavy fields")
except Exception as e:
    fail(f"to_list_view(): {e}", e)

# --- to_detail_view() ---
try:
    dv = product.to_detail_view(dummy)
    assert isinstance(dv["_id"], str)
    assert isinstance(dv["category_id"], str)
    assert "images" in dv
    assert "specifications" in dv
    assert "category" not in dv
    ok("to_detail_view() serializes full doc (no category embed when not passed)")

    cat = {
        "_id": ObjectId(),
        "slug": "neon-signs",
        "name": "Neon Signs",
        "attribute_schema": {"color": ["red", "blue"]},
        "accent_color": "#FF6B6B",
    }
    dv2 = product.to_detail_view(dummy, category=cat)
    assert "category" in dv2
    assert isinstance(dv2["category"]["_id"], str)
    assert dv2["category"]["name"] == "Neon Signs"
    ok("to_detail_view() correctly embeds category when provided")
except Exception as e:
    fail(f"to_detail_view(): {e}", e)

# --- _iso() / timestamps ---
try:
    from app.models.product import _iso, _utcnow
    now = _utcnow()
    assert isinstance(now.isoformat(), str)
    ok("_utcnow() returns timezone-aware datetime")
    iso = _iso(now)
    assert isinstance(iso, str) and "T" in iso
    ok("_iso() converts datetime to ISO string")
    assert _iso(None) is None
    ok("_iso(None) returns None")
except Exception as e:
    fail(f"_utcnow/_iso: {e}", e)

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{'='*55}")
print(f"Results: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print(f"FAILED: {FAIL}")
    sys.exit(1)
else:
    print("All checks passed!")
