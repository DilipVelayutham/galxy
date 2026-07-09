import os
import logging

logger = logging.getLogger(__name__)

# Cloudinary URL environment variable
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

def upload_image_to_cloudinary(file_path_or_stream, folder="galxy_custom"):
    """
    Helper function to upload image files to Cloudinary.
    Requires the 'cloudinary' package to be installed:
        pip install cloudinary
    
    The Cloudinary SDK automatically configures itself using the CLOUDINARY_URL
    environment variable loaded from your .env file.

    Usage example:
        from utils.cloudinary_helper import upload_image_to_cloudinary
        image_url = upload_image_to_cloudinary(file, folder="products")
    """
    if not CLOUDINARY_URL or "<your_api_key>" in CLOUDINARY_URL:
        logger.warning("Cloudinary URL is not configured or contains placeholder keys in your .env file.")
        return None
        
    try:
        import cloudinary
        import cloudinary.uploader
        
        # The cloudinary SDK loads the CLOUDINARY_URL env var automatically on import,
        # but we can also set it explicitly just in case:
        cloudinary.config(cloudinary_url=CLOUDINARY_URL)
        
        response = cloudinary.uploader.upload(
            file_path_or_stream,
            folder=folder,
            overwrite=True,
            resource_type="image"
        )
        return response.get("secure_url")
    except ImportError:
        logger.error("Cloudinary library is not installed. Add 'cloudinary' to requirements.txt.")
        return None
    except Exception as e:
        logger.error(f"Error uploading image to Cloudinary: {e}")
        return None
