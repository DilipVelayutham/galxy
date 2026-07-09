from flask import Flask
from app.db import init_db

def create_app(testing=False, mock_client=None):
    """
    Flask Application Factory.
    Registers blueprints and initializes database connections.
    """
    app = Flask(__name__)
    app.config["TESTING"] = testing
    
    # Initialize database connection
    init_db(app=app, testing=testing, mock_client=mock_client)
    
    # Register blueprints
    from app.routes.cart_routes import cart_bp
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    
    return app
