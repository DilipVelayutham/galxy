from flask import Flask, jsonify
from flask_cors import CORS
from app.routes.ai_routes import ai_blueprint
from app.routes.admin_ai_routes import admin_ai_blueprint
from app.database import init_indexes

def create_app():
    """Flask Application Factory."""
    app = Flask(__name__)
    
    # Configure CORS for frontend access
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(ai_blueprint)
    app.register_blueprint(admin_ai_blueprint)
    
    # Initialize MongoDB Indexes on startup
    with app.app_context():
        init_indexes()
        
    @app.route('/')
    def index():
        return jsonify({
            "service": "Galxy Module 5 AI Preview Generation Backend API",
            "version": "1.0.0",
            "status": "online",
            "endpoints": {
                "POST": "/api/ai/generate-preview",
                "GET_history": "/api/ai/generations/<user_id>",
                "GET_admin": "/api/admin/ai/generations"
            }
        })
        
    return app
