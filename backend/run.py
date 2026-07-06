import os
import sys

# Ensure backend root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    # Run the Flask app on all interfaces at port 5000
    app.run(host='0.0.0.0', port=port, debug=True)
