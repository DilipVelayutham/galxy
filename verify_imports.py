"""
verify_imports.py -- Quick import & syntax check for Module 3.
Run: py verify_imports.py
"""

import sys

modules = [
    "config",
    "app.db",
    "app.models.product",
    "app.utils.slug_helper",
    "app.utils.search_helper",
    "app.services.product_service",
    "app.services.product_image_service",
    "app.routes.product_routes",
]

ok = True
for mod in modules:
    try:
        __import__(mod)
        print(f"  [OK]   {mod}")
    except Exception as exc:
        print(f"  [FAIL] {mod}  ->  {exc}")
        ok = False

if ok:
    print("\nAll imports OK.")
else:
    print("\nSome imports failed -- see above.")
    sys.exit(1)
