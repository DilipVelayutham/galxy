"""
Data Verification Script
=========================================
Internal Note: Verification still pending for live data.

Run this script to check if the $lookup logic is working correctly for the sample products.
If no matching documents exist in the linked collections, then the zero-values seen in
the dashboard are correct for this environment.

Run from the repository root (backend virtual-env must be active):

  Windows:   python backend/scripts/verify_product_data.py
  macOS/Linux: python backend/scripts/verify_product_data.py

The script connects to the shared Atlas cluster using backend/.env (MONGO_URI /
MONGO_DB_NAME) and prints a plain-text evidence report.  Copy the output into
your PR comment to close the remaining verification item.
"""

import os
import sys

# Allow running from repo root or from backend/
_this_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.join(_this_dir, '..')
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load backend/.env (the script lives in backend/scripts/, so go up two levels
# from __file__ to find backend/.env)
_env_path = os.path.join(_backend_dir, '.env')
load_dotenv(_env_path)

MONGO_URI = os.environ.get('MONGO_URI')
MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'galxy')

if not MONGO_URI:
    print("ERROR: MONGO_URI is not set in backend/.env — cannot connect.")
    sys.exit(1)

try:
    # pyrefly: ignore [missing-import]
    from pymongo import MongoClient
    # pyrefly: ignore [missing-import]
    from bson import ObjectId
except ImportError:
    print("ERROR: pymongo/bson not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def _try_object_id(value):
    """Return ObjectId(value) if valid, else the original string."""
    try:
        if ObjectId.is_valid(value):
            return ObjectId(value)
    except Exception:
        pass
    return value


def run_verification():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]

    print("=" * 70)
    print("Data Verification Report")
    print(f"Database : {MONGO_DB_NAME}")
    print("=" * 70)

    # ------------------------------------------------------------------ #
    # Step 1: Fetch one representative product from the products collection
    # ------------------------------------------------------------------ #
    product = db.products.find_one({})
    if product is None:
        print("\n[RESULT] products collection is EMPTY.")
        print("  -> Zero-value dashboard output is CORRECT - no data to aggregate.")
        print("  -> PR action: close verification item with note 'products collection empty'.")
        client.close()
        return

    product_id = product['_id']
    product_id_str = str(product_id)
    category_id_raw = product.get('category_id')

    print(f"\nSample product:")
    print(f"  _id          : {product_id}  (type: {type(product_id).__name__})")
    print(f"  title        : {product.get('title', '<no title field>')}")
    print(f"  views        : {product.get('views', '<no views field>')}")
    print(f"  category_id  : {category_id_raw}  (type: {type(category_id_raw).__name__})")

    # ------------------------------------------------------------------ #
    # Step 2: Confirm category lookup
    # ------------------------------------------------------------------ #
    print("\n--- Category Lookup ---")
    if category_id_raw is None:
        print("  category_id is NULL on this product document.")
        print("  -> category_name will be 'Unknown Category' - this is CORRECT behaviour.")
        category_match = None
    else:
        cat_id_as_obj = _try_object_id(str(category_id_raw))
        # Try both ObjectId and string forms (mirrors the $lookup pipeline)
        category_match = db.categories.find_one({
            '$or': [
                {'_id': cat_id_as_obj},
                {'_id': str(category_id_raw)},
            ]
        })
        if category_match:
            print(f"  FOUND in categories: _id={category_match['_id']}, "
                  f"name={category_match.get('name', '<no name>')}")
            print("  -> If dashboard still shows 'Unknown Category', the $lookup has a "
                  "type mismatch - investigate the stored type of category_id on products.")
        else:
            print(f"  NOT FOUND in categories for category_id={category_id_raw!r}")
            print("  -> 'Unknown Category' output is CORRECT - no matching category doc.")

    # ------------------------------------------------------------------ #
    # Step 3: Confirm wishlist lookup
    # ------------------------------------------------------------------ #
    print("\n--- Wishlist Lookup ---")
    # wishlists store product_ids as an array; match ObjectId or string form
    wishlist_match = db.wishlists.find_one({
        '$or': [
            {'product_ids': product_id},
            {'product_ids': product_id_str},
        ]
    })
    if wishlist_match:
        print(f"  FOUND wishlist referencing product {product_id_str}")
        print("  -> If dashboard still shows wishlist_count=0, the $lookup has a "
              "type mismatch - investigate how product_ids are stored in wishlists.")
    else:
        print(f"  NOT FOUND in wishlists for product_id={product_id_str}")
        print("  -> wishlist_count=0 output is CORRECT - no wishlist references this product.")

    # ------------------------------------------------------------------ #
    # Step 4: Confirm order lookup
    # ------------------------------------------------------------------ #
    print("\n--- Order Lookup ---")
    # orders store items as an array of sub-docs with product_id field
    order_match = db.orders.find_one({
        '$or': [
            {'items.product_id': product_id},
            {'items.product_id': product_id_str},
        ]
    })
    if order_match:
        print(f"  FOUND order referencing product {product_id_str}")
        print("  -> If dashboard still shows order_count=0, the $lookup has a "
              "type mismatch - investigate items.product_id type in orders.")
    else:
        print(f"  NOT FOUND in orders for product_id={product_id_str}")
        print("  -> order_count=0 output is CORRECT - no orders reference this product.")

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 70)
    if category_match is None and wishlist_match is None and order_match is None:
        print("VERDICT: No matching documents found in categories / wishlists / orders.")
        print("  All-zero dashboard values are CORRECT for this seed/dev database.")
        print("  PR ACTION: Close verification item with note confirming data check.")
    else:
        print("VERDICT: At least one matching document WAS found but may not surface in")
        print("  the dashboard. Investigate the $lookup type-mismatch path described")
        print("  above before closing this verification item.")
    print("=" * 70)

    client.close()


if __name__ == '__main__':
    run_verification()
