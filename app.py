import os
from flask import Flask, jsonify
from db import init_all_indexes
from routes.cart import cart_bp
from routes.configurator import configurator_bp

# Initialize Flask application
app = Flask(__name__)

# Register Blueprints
app.register_blueprint(cart_bp)
app.register_blueprint(configurator_bp)

# Set up indexes on startup (skip if running tests)
if not os.getenv("TESTING"):
    with app.app_context():
        init_all_indexes()

# Standard JSON error handlers for general HTTP errors
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({
        "success": False,
        "message": "The requested resource was not found on this server.",
        "errors": {"route": "Not Found"}
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "success": False,
        "message": "The method is not allowed for the requested URL.",
        "errors": {"method": "Method Not Allowed"}
    }), 405

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        "success": False,
        "message": "An internal server error occurred.",
        "errors": {"server": "Internal Server Error"}
    }), 500

@app.route("/")
def index():
    """
    Base server health check
    """
    return jsonify({
        "success": True,
        "message": "GALXY Custom Lighting & Craft Studio Backend API is online.",
        "data": {
            "status": "healthy",
            "version": "1.0.0"
        }
    }), 200

if __name__ == "__main__":
    # Run the application (default to port 5000)
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
