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
    from app.db import init_db
    if test_config:
        app.config.update(test_config)
    
    if app.config.get('TESTING') or (test_config and test_config.get('MOCK_DB')):
        app.config['TESTING'] = True
        if 'MONGO_CLIENT' not in app.config:
            import mongomock
            app.config['MONGO_CLIENT'] = mongomock.MongoClient()
            app.config['DATABASE_NAME'] = os.getenv("DATABASE_NAME", "galxy_test")

    db = init_db(app)
    import sys
    sys.modules[__name__].db = db
            
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.admin_auth_routes import admin_auth_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(admin_auth_bp, url_prefix='/api/admin/auth')
    
    return app
