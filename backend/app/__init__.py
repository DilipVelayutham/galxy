"""
__init__.py — Module 5 Flask application factory
Creates and configures the Flask app, registers blueprints, and ensures
MongoDB indexes are created at startup.
"""
import logging
import os
from flask import Flask, jsonify
from flask_cors import CORS

from app.models.ai_generation import ensure_indexes
from app.routes.ai_routes import ai_bp, ai_blueprint
from app.routes.admin_ai_routes import admin_ai_bp, admin_ai_blueprint

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def create_app() -> Flask:
    """Flask Application Factory (spec §9)."""
    app = Flask(__name__)

    # ── CORS ───────────────────────────────────────────────────────────────────────
    # Allow the GALXY frontend (React/Next.js) to call this backend.
    # Tighten origins in production to the deployed frontend URL.
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
    CORS(app, resources={r"/api/*": {"origins": frontend_origin}})

    # ── Register blueprints ────────────────────────────────────────────────────────
    # Legacy blueprints take precedence for compatibility with legacy test_suite.py
    app.register_blueprint(ai_blueprint)
    app.register_blueprint(admin_ai_blueprint)

    # Modern blueprints fallback/handle remaining routes
    try:
        app.register_blueprint(ai_bp)
    except AssertionError:
        pass

    try:
        app.register_blueprint(admin_ai_bp)
    except AssertionError:
        pass

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
        return jsonify({"status": "ok", "module": "5 - AI Preview Generation"}), 200

    return app
