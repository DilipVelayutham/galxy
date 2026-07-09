"""
Quick script to verify MongoDB Atlas connectivity.
Run: py scripts/test_connection.py
"""
import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient  # noqa: E402
from pymongo.errors import ConnectionFailure, ConfigurationError  # noqa: E402

MONGO_URI = os.environ.get("MONGO_URI", "")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "galaxy_pro")

if "<db_password>" in MONGO_URI:
    print("[ERROR] Replace <db_password> in your .env file with your actual Atlas password.")
    sys.exit(1)

print("[INFO] Connecting to MongoDB Atlas ...")
print(f"    URI  : {MONGO_URI[:50]}...")
print(f"    DB   : {MONGO_DB_NAME}\n")

try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=8_000,
        connectTimeoutMS=8_000,
    )
    # Force actual handshake
    info = client.server_info()
    db = client[MONGO_DB_NAME]
    collections = db.list_collection_names()

    print("[OK] Connected successfully!")
    print(f"    MongoDB version : {info.get('version', 'unknown')}")
    print(f"    Database        : {MONGO_DB_NAME}")
    print(f"    Collections     : {collections if collections else '(none yet)'}")
    client.close()

except ConfigurationError as e:
    print(f"[ERROR] Configuration error: {e}")
    sys.exit(1)
except ConnectionFailure as e:
    print(f"[ERROR] Connection failed: {e}")
    print("\n   Common fixes:")
    print("   1. Check your password in .env")
    print("   2. Whitelist your IP in Atlas -> Network Access")
    print("   3. Verify the cluster hostname is correct")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    sys.exit(1)
