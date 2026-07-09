from app import create_app
from app.db import db
from flask_cors import CORS

app = create_app()

# Enable CORS so Next.js on port 3000 can talk to this Flask API on port 5000
CORS(app, resources={r"/api/*": {"origins": "*"}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
