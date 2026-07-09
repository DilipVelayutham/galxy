"""
app/__init__.py — Flask application factory.
"""

import cloudinary
from flask import Flask

from config import get_config
from app.db import init_db
from app.models.product import create_indexes


def create_app() -> Flask:
    """Create, configure, and return the Flask application."""
    app = Flask(__name__)

    # Load config
    cfg = get_config()
    app.config.from_object(cfg)

    # ── MongoDB ──────────────────────────────────────────────────────────
    db = init_db(app)

    # Ensure MongoDB indexes exist at startup (idempotent).
    # Wrapped in try/except: if MongoDB is not yet running the server still
    # starts; indexes will be created on the first successful connection.
    with app.app_context():
        try:
            create_indexes(db)
        except Exception as exc:
            import warnings
            warnings.warn(
                f"[Module 3] MongoDB not reachable at startup — indexes not created: {exc}\n"
                "Start MongoDB and restart (or the app will retry on first DB call).",
                RuntimeWarning,
                stacklevel=2,
            )

    # ── Cloudinary ────────────────────────────────────────────────────────
    cloudinary.config(
        cloud_name=cfg.CLOUDINARY_CLOUD_NAME,
        api_key=cfg.CLOUDINARY_API_KEY,
        api_secret=cfg.CLOUDINARY_API_SECRET,
        secure=True,
    )

    # ── Blueprints ────────────────────────────────────────────────────────
    from app.routes.product_routes import product_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(product_bp)
    app.register_blueprint(admin_bp)

    # Health-check endpoint (useful for load balancers / CI)
    @app.get("/api/health")
    def health():
        return {"success": True, "module": "products", "status": "ok"}

    return app
