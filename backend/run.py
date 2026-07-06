import os
import sys

# Ensure both workspace root and backend root are in Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
workspace_dir = os.path.dirname(backend_dir)

if backend_dir not in sys.path:
    sys.path.append(backend_dir)

if workspace_dir not in sys.path:
    sys.path.append(workspace_dir)

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)