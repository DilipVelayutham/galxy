from flask import Flask, jsonify
import logging
import os
from app.config import Config
from app.db import Database
from app.routes.site_content_routes import public_bp as public_site_content_bp
from app.routes.admin_site_content_routes import admin_bp as admin_site_content_bp
from app.routes.media_routes import media_bp

from app.routes.auth_routes import auth_bp
from app.routes.admin_auth_routes import admin_auth_bp
from app.routes.category_routes import category_bp
from app.routes.product_routes import product_bp
from app.routes.admin_product_routes import admin_product_bp
from app.routes.configurator_routes import configurator_bp
from app.routes.ai_routes import ai_blueprint
from app.routes.admin_ai_routes import admin_ai_blueprint
from app.routes.cart_routes import cart_bp
from app.routes.wishlist_routes import wishlist_bp
from app.routes.order_routes import order_routes
from app.routes.admin_order_routes import admin_bp as admin_orders_bp
from app.routes.review_routes import review_bp
from app.routes.admin_review_routes import admin_review_bp
from app.routes.testimonial_routes import testimonial_bp
from app.routes.admin_testimonial_routes import admin_testimonial_bp
from app.routes.notification_routes import notification_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.admin_dashboard_routes import admin_dashboard_bp
from app.routes.sri_routes import sri_bp
from app.routes.user_routes import user_bp


logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """
    Application Factory to bootstrap the Flask application.
    """
    app = Flask(__name__)
    if isinstance(config_class, dict):
        app.config.from_mapping(config_class)
    else:
        app.config.from_object(config_class)

    import sys
    if "pytest" in sys.modules or os.getenv("TESTING") == "True":
        app.config['TESTING'] = True

    # Reset database cache in testing to ensure isolation between test runs
    if app.config.get('TESTING'):
        Database._client = None
        Database._db = None
        
        # Clear leaked mock attributes from the app.db module
        import sys
        mod = sys.modules.get('app.db')
        if mod:
            for attr in list(mod.__dict__.keys()):
                val = mod.__dict__[attr]
                if 'mock' in str(type(val)).lower():
                    delattr(mod, attr)

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
    app.register_blueprint(public_site_content_bp)
    app.register_blueprint(admin_site_content_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_auth_bp, url_prefix="/api/admin/auth")
    app.register_blueprint(category_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(admin_product_bp, url_prefix="/api/admin")
    app.register_blueprint(configurator_bp, url_prefix="/api/configurator")
    app.register_blueprint(ai_blueprint, url_prefix="/api/ai")
    app.register_blueprint(admin_ai_blueprint, url_prefix="/api/admin/ai")
    app.register_blueprint(cart_bp, url_prefix="/api")
    app.register_blueprint(wishlist_bp, url_prefix="/api")
    app.register_blueprint(order_routes)
    app.register_blueprint(admin_orders_bp, url_prefix="/api/admin")
    app.register_blueprint(review_bp, url_prefix="/api")
    app.register_blueprint(admin_review_bp, url_prefix="/api/admin")
    app.register_blueprint(testimonial_bp)
    app.register_blueprint(admin_testimonial_bp)
    app.register_blueprint(notification_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(sri_bp)
    app.register_blueprint(user_bp, url_prefix="/api/user")



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
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Vary'] = 'Origin'
            else:
                allowed_origins = [o.strip() for o in allowed_origins_raw.split(',') if o.strip()]
                if origin in allowed_origins:
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Vary'] = 'Origin'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
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
