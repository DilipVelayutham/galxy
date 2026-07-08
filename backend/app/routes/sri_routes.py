from flask import Blueprint, request, jsonify
from app.db import db
from app.services.pricing_service import calculate_custom_price

sri_bp = Blueprint("sri", __name__)

@sri_bp.route("/", methods=["GET"])
def home_status():
    db_status = "JSON File Fallback Database" if db.is_fallback else "MongoDB Database"
    return f"""
    <html>
        <head>
            <title>GALXY API Server</title>
            <style>
                body {{
                    background: #050508;
                    color: #f3f3f6;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .status-card {{
                    background: rgba(13, 13, 22, 0.8);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    padding: 3rem;
                    border-radius: 20px;
                    text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                    max-width: 450px;
                }}
                h1 {{
                    color: #00f3ff;
                    margin: 0.5rem 0 1.5rem 0;
                    font-size: 1.8rem;
                    letter-spacing: 1px;
                }}
                .status-badge {{
                    background: #00ff66;
                    color: #020206;
                    padding: 0.3rem 0.8rem;
                    border-radius: 40px;
                    font-weight: 700;
                    font-size: 0.8rem;
                    display: inline-block;
                    letter-spacing: 1px;
                }}
                p {{
                    color: #8e90a6;
                    line-height: 1.6;
                    margin: 0.8rem 0;
                }}
                a {{
                    color: #00f3ff;
                    text-decoration: none;
                    font-weight: 600;
                    transition: all 0.3s ease;
                }}
                a:hover {{
                    text-shadow: 0 0 8px #00f3ff;
                }}
            </style>
        </head>
        <body>
            <div class="status-card">
                <span class="status-badge">ONLINE</span>
                <h1>GALXY API SERVER</h1>
                <p>The backend services are running successfully on port <strong>5000</strong>.</p>
                <p>Database Connection: <strong style="color: #f3f3f6;">{db_status}</strong></p>
                <p style="margin-top: 2rem; font-size: 0.95rem;">
                    Launch the visualizer app at: <br/>
                    <a href="http://localhost:3000" target="_blank">http://localhost:3000</a>
                </p>
            </div>
        </body>
    </html>
    """

@sri_bp.route("/api/price", methods=["POST"])
def get_price():
    try:
        config = request.json or {}
        settings = db.get_admin_settings()
        computed_price = calculate_custom_price(config, settings)
        return jsonify({
            "success": True,
            "price": computed_price
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@sri_bp.route("/api/config", methods=["POST"])
def save_config():
    try:
        config_data = request.json or {}
        
        # Calculate final price on backend for verification/security
        settings = db.get_admin_settings()
        config_data["price"] = calculate_custom_price(config_data, settings)
        
        saved_config = db.save_configuration(config_data)
        return jsonify({
            "success": True,
            "configuration": saved_config
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@sri_bp.route("/api/config", methods=["GET"])
def get_configs():
    try:
        configs = db.get_configurations()
        return jsonify({
            "success": True,
            "configurations": configs
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@sri_bp.route("/api/config/<config_id>", methods=["DELETE"])
def delete_config(config_id):
    try:
        success = db.delete_configuration(config_id)
        return jsonify({
            "success": success
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@sri_bp.route("/api/admin/settings", methods=["GET"])
def get_settings():
    try:
        settings = db.get_admin_settings()
        return jsonify({
            "success": True,
            "settings": settings
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@sri_bp.route("/api/admin/settings", methods=["POST"])
def update_settings():
    try:
        new_settings = request.json or {}
        updated = db.update_admin_settings(new_settings)
        return jsonify({
            "success": True,
            "settings": updated
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
