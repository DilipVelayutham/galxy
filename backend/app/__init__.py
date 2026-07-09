from flask import Flask
from flask_cors import CORS

from app.configs.env_config import Config
from app.database.db import db

def create_app(config_class=Config):
    """Application factory for the GALXY backend."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)

    # CORS configuration
    CORS(app, supports_credentials=True)

    # Initialize Database connection
    # Avoid initializing if we're in mock-test environment or db is bypassed
    if not app.config.get("TESTING"):
        try:
            db.init_app(app)
        except Exception as e:
            app.logger.error(f"Failed to initialize database: {e}")

    # Register blueprints
    from app.routes.testimonial_routes import testimonial_bp
    from app.routes.admin_testimonial_routes import admin_testimonial_bp

    app.register_blueprint(testimonial_bp)
    app.register_blueprint(admin_testimonial_bp)

    # Generic health check
    from app.utils.response_helper import success_response, error_response
    
    @app.route("/api/health", methods=["GET"])
    def health():
        return success_response({"status": "ok"}, "Galxy Testimonials sub-module is running.")

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return error_response("The requested endpoint does not exist.", status_code=404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response("HTTP method not allowed on this endpoint.", status_code=405)

    @app.errorhandler(500)
    def internal_error(e):
        return error_response("An internal server error occurred.", status_code=500)

    return app
