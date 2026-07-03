"""
__init__.py — Module 5 Flask application factory
Creates and configures the Flask app, registers blueprints, and ensures
MongoDB indexes are created at startup.
"""
import logging
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
    CORS(app, resources={r"/api/*": {"origins": "*"}})

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

    return app
