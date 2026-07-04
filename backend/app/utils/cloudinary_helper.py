"""
cloudinary_helper.py — Module 5 Shared Utility
Consolidated helper for Cloudinary uploads.

Can be shared with Modules 3 and 10 to consolidate Cloudinary configuration
and prevent duplicate wrappers.
"""
import io
import time
import cloudinary
import cloudinary.uploader
from app.configs.ai_config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
    CLOUDINARY_AI_PREVIEW_FOLDER,
)

_initialized = False


def init_cloudinary():
    """Configure the Cloudinary SDK if not already done."""
    global _initialized
    if not _initialized:
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True,
        )
        _initialized = True


def upload_preview_image(image_bytes: bytes, category_id: str) -> str:
    """
    Upload raw image bytes to Cloudinary under the dedicated folder (spec §10).

    Returns:
        The secure URL of the uploaded image.
    """
    init_cloudinary()
    public_id = f"{CLOUDINARY_AI_PREVIEW_FOLDER}/gen_{category_id}_{int(time.time())}"
    result = cloudinary.uploader.upload(
        io.BytesIO(image_bytes),
        public_id=public_id,
        resource_type="image",
        overwrite=False,
        unique_filename=True,
    )
    url: str = result.get("secure_url", "")
    if not url:
        raise RuntimeError(
            "Cloudinary upload returned no secure_url. Response: " + str(result)
        )
    return url
