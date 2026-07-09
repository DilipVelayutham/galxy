from flask import Flask, jsonify
import logging
from config import Config
from app.db import Database
from app.routes.site_content_routes import public_bp
from app.routes.admin_site_content_routes import admin_bp
from app.routes.media_routes import media_bp

logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """
    Application Factory to bootstrap the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Security hygiene check for hardcoded default fallback keys
    if app.config.get('SECRET_KEY') == 'default-flask-secret-key-galxy':
        logger.warning("SECURITY WARNING: Using default hardcoded SECRET_KEY! Please configure SECRET_KEY in environment variables.")
    if app.config.get('JWT_SECRET') == 'super_secret_jwt_key_for_galxy_cms':
        logger.warning("SECURITY WARNING: Using default hardcoded JWT_SECRET! Please configure JWT_SECRET in environment variables.")

    # Initialize MongoDB Collections & Indexes on startup
    with app.app_context():
        try:
            Database.init_db()
            import sys
            if "pytest" not in sys.modules:
                db = Database.get_db()
                if Database._is_mock or db['site_content'].count_documents({}) == 0:
                    logger.info("Database is empty or running on mock. Auto-seeding default site content...")
                    from scripts.seed_site_content import seed_database
                    seed_database()
        except Exception as e:
            logger.error(f"Could not initialize database on startup: {e}")

    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(media_bp)


    # Enable CORS headers
    @app.after_request
    def add_cors_headers(response):
        # NOTE: CORS wildcard '*' is used for local integration and staging. 
        # For production, specify allowed origins separated by commas in CORS_ALLOWED_ORIGINS.
        from flask import request
        origin = request.headers.get('Origin')
        if origin:
            allowed_origins_raw = app.config.get('CORS_ALLOWED_ORIGINS', '*')
            if allowed_origins_raw == '*':
                response.headers['Access-Control-Allow-Origin'] = '*'
            else:
                allowed_origins = [o.strip() for o in allowed_origins_raw.split(',') if o.strip()]
                if origin in allowed_origins:
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Vary'] = 'Origin'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        return response

    # Global Error Handlers for standardized JSON envelopes
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({
            "success": False,
            "data": None,
            "message": "The requested resource was not found."
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            "success": False,
            "data": None,
            "message": "The HTTP method is not allowed for this endpoint."
        }), 405

    @app.errorhandler(413)
    def payload_too_large(e):
        logger.warning("Request payload exceeded MAX_CONTENT_LENGTH limit.")
        return jsonify({
            "success": False,
            "data": None,
            "message": "File size exceeds the maximum limit of 5 MB.",
            "errors": ["RequestEntityTooLarge"]
        }), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({
            "success": False,
            "data": None,
            "message": "An internal server error occurred."
        }), 500

    return app
