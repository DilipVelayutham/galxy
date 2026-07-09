import os
import logging
from app import create_app

# Configure application-wide logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    logger.info(f"Starting Galxy CMS Backend on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
