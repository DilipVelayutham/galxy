import os
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Setup MongoDB Atlas connection
mongo_uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("MONGO_DB_NAME", "galxy")

# Global DB reference accessed by services
if mongo_uri:
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
    except Exception:
        db = None
else:
    db = None

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable Cross-Origin Resource Sharing for frontend Next.js requests
    
    # Import and register routes blueprint
    from app.routes.admin_dashboard_routes import admin_dashboard_bp
    app.register_blueprint(admin_dashboard_bp)
    
    return app
