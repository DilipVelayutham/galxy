from flask import Flask
from pymongo import MongoClient
import cloudinary
from app.configs.ai_config import AIConfig

db = None

def create_app(config_class=AIConfig):
    global db
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize MongoDB Client
    client = MongoClient(app.config["MONGO_URI"])
    db = client.get_default_database()
    
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
    
    # Create indexes
    from app.models.ai_generation import AIGeneration
    try:
        AIGeneration.create_indexes()
    except Exception as e:
        app.logger.warning(f"Could not create database indexes: {e}")
    
    return app
