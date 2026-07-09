import logging
import time
from flask import g, has_request_context
from werkzeug.utils import secure_filename
from PIL import Image
from config import Config
from app.utils.cloudinary_helper import upload_image, delete_image
from app.utils.exceptions import (
    MissingFileError,
    InvalidFolderError,
    InvalidExtensionError,
    InvalidMimeTypeError,
    FileSizeExceededError,
    CloudinaryUploadError,
    CloudinaryTimeoutError,
    CorruptedImageError,
    InvalidImageDimensionsError
)
from cloudinary.exceptions import Error as CloudinaryError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _should_retry(exception: Exception) -> bool:
    """
    Determines if a Cloudinary upload failure is transient and should be retried.
    We do not retry for invalid client configurations, invalid file formats,
    or auth failures.
    """
    err_msg = str(exception).lower()
    non_retryable_keywords = [
        "invalid", "bad request", "must be", "unauthorized", "api_key",
        "signature", "credentials", "format not supported", "empty file"
    ]
    if isinstance(exception, CloudinaryError):
        if any(kw in err_msg for kw in non_retryable_keywords):
            return False
    return True


def _is_timeout(exception: Exception) -> bool:
    """Checks if the exception was caused by a timeout."""
    class_name = exception.__class__.__name__.lower()
    if "timeout" in class_name:
        return True
    if "timeout" in str(exception).lower():
        return True
    return False


def get_request_id() -> str:
    """Helper to safely retrieve the current Flask request ID."""
    if has_request_context() and hasattr(g, "request_id"):
        return g.request_id
    return "SYSTEM"


def upload_to_folder(file, folder_name: str) -> str:
    """
    Validates the uploaded file and destination folder, then uploads the file to Cloudinary.

    Args:
        file: The file object from Flask's request.files (typically a Werkzeug FileStorage object).
        folder_name: The destination folder whitelisted in Config.

    Returns:
        str: The secure Cloudinary URL as a plain string.

    Raises:
        MissingFileError: If the file is not provided or empty.
        InvalidFolderError: If the folder name is not in the whitelist.
        InvalidExtensionError: If the file extension is not allowed.
        InvalidMimeTypeError: If the file MIME type is not allowed.
        FileSizeExceededError: If the file size exceeds the maximum limit (5MB).
        CorruptedImageError: If the image file is corrupted or unreadable.
        InvalidImageDimensionsError: If the image dimensions are <= 0.
        CloudinaryTimeoutError: If the upload operation to Cloudinary times out.
        CloudinaryUploadError: If the upload operation to Cloudinary fails after retries.
    """
    # 1. Validate file existence
    if file is None or not getattr(file, "filename", ""):
        logger.error(
            f"[{get_request_id()}] Upload attempt failed: File object is missing or has an empty filename.")
        raise MissingFileError()

    original_filename = file.filename

    # Sanitize uploaded filename
    filename = secure_filename(original_filename)
    if not filename:
        ext = original_filename.rsplit(
            ".", 1)[1].lower() if "." in original_filename else ""
        filename = f"file_{int(time.time())}.{ext}" if ext else f"file_{int(time.time())}"

    # Assign the sanitized filename back to the file object
    file.filename = filename

    logger.info(
        f"[{get_request_id()}] Received upload request for file '{original_filename}' (sanitized: '{filename}') into folder '{folder_name}'.")

    # 2. Validate folder name against whitelist
    if folder_name not in Config.VALID_FOLDERS:
        logger.error(
            f"[{get_request_id()}] Upload attempt failed: Folder '{folder_name}' is not in the whitelist.")
        raise InvalidFolderError(folder_name, Config.VALID_FOLDERS)

    # 3. Validate file extension
    if "." not in filename:
        logger.error(
            f"[{get_request_id()}] Upload attempt failed: Filename '{filename}' does not contain an extension.")
        raise InvalidExtensionError("", Config.ALLOWED_FORMATS)

    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in Config.ALLOWED_FORMATS:
        logger.error(
            f"[{get_request_id()}] Upload attempt failed: Extension '{ext}' is not supported.")
        raise InvalidExtensionError(ext, Config.ALLOWED_FORMATS)

    # Validate MIME type via request content_type header
    content_type = getattr(file, "content_type", "")
    if not content_type or content_type not in Config.ALLOWED_MIME_TYPES:
        logger.error(
            f"[{get_request_id()}] Upload attempt failed: MIME type '{content_type}' is not supported.")
        raise InvalidMimeTypeError(content_type, Config.ALLOWED_MIME_TYPES)

    # 4. Validate file size
    try:
        # Seek to the end to get length, then seek back to start
        file.seek(0, 2)
        size_bytes = file.tell()
        file.seek(0)
    except Exception as e:
        logger.error(f"[{get_request_id()}] Failed to read file size: {e}")
        raise MissingFileError("Could not read the uploaded file stream.")

    if size_bytes > Config.MAX_FILE_SIZE_BYTES:
        size_mb = size_bytes / (1024 * 1024)
        logger.error(
            f"[{get_request_id()}] Upload attempt failed: File size ({size_mb:.2f} MB) exceeds limit of {Config.MAX_FILE_SIZE_MB} MB.")
        raise FileSizeExceededError(size_mb, Config.MAX_FILE_SIZE_MB)

    # 5. Image Validation using Pillow
    try:
        # Read file into Pillow to verify integrity
        img = Image.open(file)
        img.verify()

        # Re-seek and open image again since verify() invalidates the stream for size checking
        file.seek(0)
        img = Image.open(file)
    except Exception as e:
        logger.error(
            f"[{get_request_id()}] Upload attempt failed: File '{filename}' is corrupted or not a valid image. Error: {e}")
        raise CorruptedImageError(
            f"The uploaded file '{filename}' is corrupted or not a valid image.")

    # Validate image format matches expected MIME type
    img_format = img.format.lower() if img.format else ""
    FORMAT_TO_MIME = {
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp"
    }
    detected_mime = FORMAT_TO_MIME.get(img_format, "")
    if not detected_mime or detected_mime not in Config.ALLOWED_MIME_TYPES:
        logger.error(
            f"[{get_request_id()}] Upload attempt failed: Image format '{img_format}' (MIME: '{detected_mime}') is not allowed.")
        raise InvalidMimeTypeError(
            detected_mime or img_format, Config.ALLOWED_MIME_TYPES)

    # Validate dimensions (width/height > 0)
    width, height = img.size
    if width <= 0 or height <= 0:
        logger.error(
            f"[{get_request_id()}] Upload attempt failed: Image dimensions {width}x{height} are invalid.")
        raise InvalidImageDimensionsError(
            "Image dimensions must be greater than zero.")

    logger.info(
        f"[{get_request_id()}] Image validation passed. Format: {img_format}, Dimensions: {width}x{height}.")
    file.seek(0)

    # 6. Call Cloudinary Helper to upload the image with retry logic
    max_retries = 3
    upload_details = None
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            # Always reset file pointer before each upload attempt
            file.seek(0)
            logger.info(
                f"[{get_request_id()}] Uploading '{filename}' to Cloudinary (attempt {attempt + 1}/{max_retries + 1})...")
            upload_details = upload_image(file, folder=folder_name, timeout=30)
            break
        except Exception as e:
            last_exception = e
            if attempt < max_retries and _should_retry(e):
                backoff_delay = 2 ** attempt
                logger.warning(
                    f"[{get_request_id()}] Cloudinary upload attempt {attempt + 1} failed: {e}. Retrying in {backoff_delay}s...")
                time.sleep(backoff_delay)
            else:
                logger.error(
                    f"[{get_request_id()}] Cloudinary upload failed: {e}")
                break

    if not upload_details:
        if _is_timeout(last_exception):
            raise CloudinaryTimeoutError(
                f"Cloudinary upload service timed out after {max_retries + 1} attempts. Error: {last_exception}")
        raise CloudinaryUploadError(
            f"Cloudinary upload service failed after {max_retries + 1} attempts. Error: {last_exception}")

    logger.info(
        f"[{get_request_id()}] Upload successful. URL: {upload_details['url']}, Public ID: {upload_details['public_id']}")
    return upload_details["url"]


def delete_from_cloudinary(public_id: str) -> bool:
    """
    Deletes an asset from Cloudinary by its public ID.

    Args:
        public_id: The public ID of the image to delete.

    Returns:
        bool: True if deleted successfully, False otherwise.
    """
    if not public_id:
        logger.error("Deletion attempt failed: Public ID is empty.")
        return False

    try:
        logger.info(
            f"Attempting to delete image with public ID '{public_id}'...")
        success = delete_image(public_id)
        if success:
            logger.info(
                f"Successfully deleted image '{public_id}' from Cloudinary.")
            return True
        else:
            logger.warning(
                f"Delete response for '{public_id}' was not successful.")
            return False
    except Exception as e:
        logger.error(f"Failed to delete image '{public_id}': {e}")
        return False
