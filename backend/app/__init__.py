from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.db import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure CORS - allow localhost:3000 (Next.js frontend)
    CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
    
    @app.route("/health")
    def health_check():
        try:
            # Quick database ping
            db.command("ping")
            return jsonify({"success": True, "message": "Server is healthy", "database": "connected"}), 200
        except Exception as e:
            return jsonify({"success": False, "message": "Database connection failed", "error": str(e)}), 500
            
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
    app.register_blueprint(testimonial_bp, url_prefix="/api")
    app.register_blueprint(admin_testimonial_bp, url_prefix="/api/admin")
    app.register_blueprint(content_bp, url_prefix="/api")
    app.register_blueprint(notification_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api/admin")
    
    return app
