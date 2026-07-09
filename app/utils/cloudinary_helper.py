import cloudinary
import cloudinary.uploader
from config import Config

# Initialize Cloudinary Configuration
cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET,
    secure=True
)


def upload_image(file_or_url, folder: str, tags: list[str] | None = None, timeout: int = 30) -> dict:
    """
    Uploads a file-like object, file path, or URL to Cloudinary in the specified folder.

    Args:
        file_or_url: A file-like object, file path, or remote URL to upload.
        folder: The destination folder in Cloudinary.
        tags: Optional list of tags to associate with the uploaded image.
        timeout: The timeout duration in seconds for the request.

    Returns:
        dict: A dictionary containing:
            - url: The secure URL of the uploaded image.
            - public_id: The unique identifier of the asset.
            - width: Width of the image.
            - height: Height of the image.
            - format: File format (e.g. png, jpg).

    Raises:
        Exception: Direct propagation of exceptions raised by the Cloudinary SDK.
    """
    params = {
        "folder": folder,
        "resource_type": "image",
        "timeout": timeout
    }
    if tags:
        params["tags"] = tags

    response = cloudinary.uploader.upload(file_or_url, **params)

    return {
        "url": response.get("secure_url"),
        "public_id": response.get("public_id"),
        "width": response.get("width"),
        "height": response.get("height"),
        "format": response.get("format")
    }


def delete_image(public_id: str) -> bool:
    """
    Deletes an asset from Cloudinary using its public ID.

    Args:
        public_id: The public ID of the image to delete.

    Returns:
        bool: True if deleted successfully, False otherwise.

    Raises:
        Exception: Direct propagation of exceptions raised by the Cloudinary SDK.
    """
    result = cloudinary.uploader.destroy(public_id)
    return result.get("result") == "ok"


def extract_public_id_from_url(url: str) -> str:
    """
    Extracts the public ID from a Cloudinary URL.
    Example:
      https://res.cloudinary.com/cloud_name/image/upload/v123456789/galxy/products/image.jpg
      -> galxy/products/image
    """
    if not url:
        return ""
    # Find the '/upload/' segment
    upload_marker = "/upload/"
    marker_idx = url.find(upload_marker)
    if marker_idx == -1:
        return ""

    # Get everything after '/upload/'
    path_after_upload = url[marker_idx + len(upload_marker):]

    # Split by '/' to see if the first segment is a version string like 'v123456789'
    parts = path_after_upload.split("/", 1)
    if len(parts) > 1 and parts[0].startswith("v") and parts[0][1:].isdigit():
        path_after_version = parts[1]
    else:
        path_after_version = path_after_upload

    # Strip the file extension
    public_id = path_after_version.rsplit(".", 1)[0]
    return public_id
