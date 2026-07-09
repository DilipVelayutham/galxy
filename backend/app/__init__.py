from flask import Flask, jsonify
from flask_cors import CORS

from app.configs.env_config import Config
from app.database.db import db

def create_app(config_class=Config):
    """Application factory for the GALXY backend."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)

    # Configure CORS - allow localhost:3000 (Next.js frontend) and supports_credentials
    CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

    # Initialize Database connection
    # Avoid initializing if we're in mock-test environment or db is bypassed
    if not app.config.get("TESTING"):
        try:
            db.init_app(app)
        except Exception as e:
            app.logger.error(f"Failed to initialize database: {e}")

    # Register blueprints (routes)
    from app.routes.auth_routes import auth_bp
    from app.routes.category_routes import category_bp
    from app.routes.product_routes import product_bp
    from app.routes.configurator_routes import configurator_bp
    from app.routes.ai_routes import ai_bp
    from app.routes.cart_routes import cart_bp
    from app.routes.wishlist_routes import wishlist_bp
    from app.routes.order_routes import order_bp
    from app.routes.review_routes import review_bp
    from app.routes.admin_review_routes import admin_review_bp
    from app.routes.testimonial_routes import testimonial_bp
    from app.routes.admin_testimonial_routes import admin_testimonial_bp
    from app.routes.content_routes import content_bp
    from app.routes.notification_routes import notification_bp
    from app.routes.dashboard_routes import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(category_bp, url_prefix="/api")
    app.register_blueprint(product_bp, url_prefix="/api")
    app.register_blueprint(configurator_bp, url_prefix="/api/configurator")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(wishlist_bp, url_prefix="/api/wishlist")
    app.register_blueprint(order_bp, url_prefix="/api")
    app.register_blueprint(review_bp, url_prefix="/api")
    app.register_blueprint(admin_review_bp, url_prefix="/api/admin")
    
    # Testimonials registered without prefix as defined in target/develop routes decorators
    app.register_blueprint(testimonial_bp)
    app.register_blueprint(admin_testimonial_bp)
    
    app.register_blueprint(content_bp, url_prefix="/api")
    app.register_blueprint(notification_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api/admin")

    # Generic health check (from target/develop)
    from app.utils.response_helper import success_response, error_response
    
    @app.route("/api/health", methods=["GET"])
    def health():
        return success_response({"status": "ok"}, "Galxy Testimonials sub-module is running.")

    # Original /health check doing a DB ping
    @app.route("/health")
    def health_check():
        try:
            # Quick database ping using initialized client
            if db.client:
                db.client.admin.command("ping")
                return jsonify({"success": True, "message": "Server is healthy", "database": "connected"}), 200
            else:
                return jsonify({"success": False, "message": "Database not initialized"}), 500
        except Exception as e:
            return jsonify({"success": False, "message": "Database connection failed", "error": str(e)}), 500

    # Global error handlers (from target/develop)
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
