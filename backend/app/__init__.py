from flask import Flask

def create_app(config: dict = None) -> Flask:
    """
    Create and configure an instance of the Flask application.
    Registers both the configurator blueprint and Sri blueprint.
    """
    app = Flask(__name__)
    if config:
        app.config.update(config)

    from app.routes.configurator_routes import configurator_bp
    from app.routes.sri_routes import sri_bp

    app.register_blueprint(configurator_bp)
    app.register_blueprint(sri_bp)

    return app
