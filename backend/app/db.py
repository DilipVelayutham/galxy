from pymongo import MongoClient
import os
import sys

client = None
db = None

def init_db(app=None):
    global client, db
    
    # Check if app is in testing mode and has a preconfigured mock client
    if app and app.config.get('TESTING') and 'MONGO_CLIENT' in app.config:
        client = app.config['MONGO_CLIENT']
        db_name = app.config.get('DATABASE_NAME', 'galxy_test')
        db = client[db_name]
        return db

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "galxy")

    # Force mock if specified in configuration
    if mongo_uri.lower() == "mock":
        print("db.py: Using mongomock.MongoClient() as requested by MONGO_URI='mock'", file=sys.stderr)
        import mongomock
        client = mongomock.MongoClient()
        db = client[db_name]
        # Auto-seed mock database if not in unit tests
        if not (app and app.config.get('TESTING')):
            try:
                from app.seed import seed_db
                print("db.py: Auto-seeding mock database...", file=sys.stderr)
                seed_db()
            except Exception as se:
                print(f"db.py: Failed to auto-seed: {se}", file=sys.stderr)
        return db

    try:
        # Try connecting with a 2-second timeout
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        # Force a connection check
        client.admin.command('ping')
        db = client[db_name]
        print(f"db.py: Connected to MongoDB at {mongo_uri}", file=sys.stderr)
    except Exception as e:
        print(f"db.py: Failed to connect to MongoDB at {mongo_uri}. Falling back to mongomock. Error: {e}", file=sys.stderr)
        import mongomock
        client = mongomock.MongoClient()
        db = client[db_name]
        # Auto-seed mock database if not in unit tests
        if not (app and app.config.get('TESTING')):
            try:
                from app.seed import seed_db
                print("db.py: Auto-seeding mock database...", file=sys.stderr)
                seed_db()
            except Exception as se:
                print(f"db.py: Failed to auto-seed: {se}", file=sys.stderr)
        
    return db

def get_db():
    global db, client
    if db is None:
        init_db()
    return db
