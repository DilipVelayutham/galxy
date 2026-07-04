import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load env variables on startup
load_dotenv()

# Database instance exposed at package level for in2/in3 runtime imports
db = None

def create_app(test_config=None):
    global db
    app = Flask(__name__)
    
    # Load defaults
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev_secret_key_12345"),
        DATABASE_NAME=os.getenv("DATABASE_NAME", "galxy"),
    )
    
    if test_config:
        app.config.from_mapping(test_config)
    
    # Initialize CORS
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    origins_list = [origin.strip() for origin in allowed_origins.split(",")]
    CORS(app, resources={r"/api/*": {"origins": origins_list}}, supports_credentials=True)
    
    # Initialize DB connection
    from app.db import init_db
    db = init_db(app)
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.admin_auth_routes import admin_auth_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(admin_auth_bp, url_prefix='/api/admin/auth')
    
    return app
