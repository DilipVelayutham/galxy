from flask import Flask
from pymongo import MongoClient
import cloudinary
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.configs.ai_config import AIConfig

db = None

def create_app(config_class=AIConfig):
    global db
    import os
    # Serve /static/* from the project root's static/ folder, not app/static/
    root_static = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    app = Flask(__name__, static_folder=root_static, static_url_path='/static')
    app.config.from_object(config_class)
    
    # Initialize MongoDB Client
    client = MongoClient(app.config["MONGO_URI"])
    try:
        db = client.get_default_database()
    except Exception:
        import os
        db_name = os.getenv("MONGO_DB_NAME", "galxy")
        db = client[db_name]
    
    # Configure Cloudinary if keys are present
    if app.config.get("CLOUDINARY_CLOUD_NAME"):
        cloudinary.config(
            cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
            api_key=app.config["CLOUDINARY_API_KEY"],
            api_secret=app.config["CLOUDINARY_API_SECRET"],
            secure=True
        )
        
    # Register blueprints
    from app.routes.ai_routes import ai_blueprint
    app.register_blueprint(ai_blueprint)
    
    from app.routes.admin_ai_routes import admin_ai_blueprint
    app.register_blueprint(admin_ai_blueprint)
    
    # Create indexes
    from app.models.ai_generation import AIGeneration
    if not app.config.get("TESTING"):
        try:
            AIGeneration.create_indexes()
        except Exception as e:
            app.logger.warning(f"Could not create database indexes: {e}")
    
    return app
