"""
Quick script to verify Cloudinary connectivity.
Run: py scripts/test_cloudinary.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import cloudinary  # noqa: E402
import cloudinary.api  # noqa: E402

CLOUD_NAME   = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
API_KEY      = os.environ.get("CLOUDINARY_API_KEY", "")
API_SECRET   = os.environ.get("CLOUDINARY_API_SECRET", "")

if not all([CLOUD_NAME, API_KEY, API_SECRET]):
    print("[ERROR] One or more Cloudinary env vars are missing in .env")
    sys.exit(1)

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
    secure=True,
)

print("[INFO] Testing Cloudinary connection ...")
print(f"    Cloud name : {CLOUD_NAME}")
print(f"    API key    : {API_KEY}\n")

try:
    result = cloudinary.api.ping()
    print("[OK] Cloudinary connected successfully!")
    print(f"    Response   : {result}")
except Exception as e:
    print(f"[ERROR] Cloudinary connection failed: {e}")
    sys.exit(1)
