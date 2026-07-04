<<<<<<< HEAD
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
        
=======
"""
__init__.py — Module 5 Flask application factory
Creates and configures the Flask app, registers blueprints, and ensures
MongoDB indexes are created at startup.
"""
import logging
import os
from flask import Flask
from flask_cors import CORS

from app.models.ai_generation import ensure_indexes
from app.routes.ai_routes import ai_bp
from app.routes.admin_ai_routes import admin_ai_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def create_app() -> Flask:
    """Application factory — create and return a configured Flask app."""
    app = Flask(__name__)

    # ── CORS ───────────────────────────────────────────────────────────────────────
    # Allow the GALXY frontend (React/Next.js) to call this backend.
    # Tighten origins in production to the deployed frontend URL.
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
    CORS(app, resources={r"/api/*": {"origins": frontend_origin}})

    # ── Register blueprints ────────────────────────────────────────────────────────
    app.register_blueprint(ai_bp)
    app.register_blueprint(admin_ai_bp)

    # ── Ensure MongoDB indexes ─────────────────────────────────────────────────────
    with app.app_context():
        try:
            ensure_indexes()
            logging.getLogger(__name__).info(
                "MongoDB indexes for ai_generations ensured."
            )
        except Exception as exc:
            logging.getLogger(__name__).warning(
                "Could not ensure MongoDB indexes at startup: %s. "
                "Check MONGO_URI in .env.",
                exc,
            )

    # ── Health check ───────────────────────────────────────────────────────────────
    @app.route("/health", methods=["GET"])
    def health():
        from flask import jsonify
        return jsonify({"status": "ok", "module": "5 - AI Preview Generation"}), 200

>>>>>>> origin/main
    return app
