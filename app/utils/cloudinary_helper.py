import re
import logging
import cloudinary
import cloudinary.uploader
from app.config import Config

logger = logging.getLogger(__name__)

# Configure Cloudinary if URL is available
if Config.CLOUDINARY_URL:
    try:
        cloudinary.config(cloudinary_url=Config.CLOUDINARY_URL)
        logger.info("Cloudinary configured successfully from CLOUDINARY_URL.")
    except Exception as e:
        logger.error(f"Failed to configure Cloudinary: {e}")
else:
    logger.warning("CLOUDINARY_URL not found in configuration. Image uploads will fail.")

def upload_to_cloudinary(file_stream, folder="galxy/products"):
    """
    Uploads an image file stream to Cloudinary under the specified folder.
    Returns:
        dict: { "url": "secure_cloudinary_url", "public_id": "cloudinary_public_id" }
    """
    try:
        logger.info(f"Uploading image to Cloudinary folder: {folder}")
        upload_result = cloudinary.uploader.upload(
            file_stream,
            folder=folder,
            overwrite=True,
            resource_type="image"
        )
        return {
            "url": upload_result.get("secure_url") or upload_result.get("url"),
            "public_id": upload_result.get("public_id")
        }
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        raise e

def delete_from_cloudinary(public_id):
    """
    Deletes an asset from Cloudinary using its public_id.
    """
    try:
        logger.info(f"Destroying Cloudinary asset: {public_id}")
        result = cloudinary.uploader.destroy(public_id)
        if result.get("result") == "ok":
            logger.info(f"Cloudinary asset {public_id} deleted successfully.")
            return True
        else:
            logger.warning(f"Cloudinary delete response was not 'ok': {result}")
            return False
    except Exception as e:
        logger.error(f"Cloudinary delete failed for public_id {public_id}: {e}")
        return False

def extract_public_id_from_url(url):
    """
    Fallback helper to parse a Cloudinary public ID from its full URL.
    Typical format:
    https://res.cloudinary.com/<cloud>/image/upload/v<version>/<folder>/<name>.<ext>
    """
    # Pattern to capture everything after /upload/ (skipping version like v12345/) up to file extension
    pattern = r"res\.cloudinary\.com/[^/]+/image/upload/(?:v\d+/)?(.+?)\.[a-zA-Z0-9]+$"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None
