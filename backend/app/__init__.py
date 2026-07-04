# ==============================================================================
# LOCAL-TESTING STUB ONLY (NOT A DELIVERABLE)
# ==============================================================================
# This __init__.py file and its create_app/CORS setup are temporary stubs
# for local testing. They are NOT owned by Module 1 (Auth Accounts) and must
# be removed or replaced by in1's integrated app at merge time.
# ==============================================================================

import os
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

# Database instance exposed at package level
db = None

def create_app(test_config=None):
    global db
    
    app = Flask(__name__)
    CORS(app)
    
    # Load env variables from backend/.env or backend/.env.example
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()
        
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default_secret_key_12345")
    
    # DB configuration
    db_name = os.getenv("DATABASE_NAME", "galxy")
    
    if test_config and test_config.get('MOCK_DB'):
        import mongomock
        client = mongomock.MongoClient()
        db = client[db_name]
    else:
        mongo_uri = os.getenv("MONGO_URI", "")
        if mongo_uri:
            client = MongoClient(mongo_uri)
            db = client[db_name]
        else:
            # Fallback to mongomock to ensure execution/tests run even without mongo installation
            print("WARNING: MONGO_URI environment variable not configured. Falling back to in-memory mongomock.")
            import mongomock
            client = mongomock.MongoClient()
            db = client[db_name]
            
    # Register blueprints
    from backend.app.routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    
    return app
