import os
from flask import Flask, jsonify
from app.config import Config
from app.db import init_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize PyMongo database
    init_db()
    
    # Register blueprints (imported locally to avoid circular import issues)
    from app.routes.review_routes import review_bp
    from app.routes.admin_review_routes import admin_review_bp
    
    app.register_blueprint(review_bp, url_prefix="/api")
    app.register_blueprint(admin_review_bp, url_prefix="/api/admin")
    
    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "message": "Bad request",
            "errors": {"info": str(error)}
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "Resource not found",
            "errors": {"info": str(error)}
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "errors": {"info": str(error)}
        }), 500
        
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "success": True,
            "message": "Service is healthy",
            "data": {"status": "healthy", "service": "reviews-backend"}
        }), 200
        
    return app
