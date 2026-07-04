import os
import sys
from pymongo import IndexModel, ASCENDING

# Ensure backend root is in the python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.db import get_db
from app.models.admin_user import AdminUser
from app.utils.password_helper import hash_password

def seed_db():
    print("Connecting to database...")
    db = get_db()
    
    # 1. Create unique indexes
    print("Creating indexes...")
    try:
        db.users.create_index([("email", ASCENDING)], unique=True)
        print("Created unique index on users.email")
    except Exception as e:
        print(f"Error creating unique index on users.email: {e}")
        
    try:
        db.admin_users.create_index([("email", ASCENDING)], unique=True)
        print("Created unique index on admin_users.email")
    except Exception as e:
        print(f"Error creating unique index on admin_users.email: {e}")

    try:
        db.users.create_index([("phone", ASCENDING)])
        print("Created index on users.phone")
    except Exception as e:
        print(f"Error creating index on users.phone: {e}")
        
    # 2. Seed default admin user for Asil
    admin_email = "admin@galxy.in"
    default_password = "AdminPassword123"
    
    print(f"Checking for existing admin account: {admin_email}...")
    existing_admin = db.admin_users.find_one({"email": admin_email})
    if existing_admin:
        print(f"Admin account {admin_email} already exists. Skipping seeding.")
    else:
        print(f"Admin account {admin_email} not found. Seeding default admin account...")
        password_hash = hash_password(default_password)
        admin_doc = AdminUser.create_document("Admin Asil", admin_email, password_hash)
        result = db.admin_users.insert_one(admin_doc)
        print(f"Admin user seeded successfully. Document ID: {result.inserted_id}")
        print(f"Default Credentials:")
        print(f"  Email: {admin_email}")
        print(f"  Password: {default_password}")
        
    print("Database seeding completed.")

if __name__ == "__main__":
    seed_db()
