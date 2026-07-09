import logging
from flask import Blueprint, request, jsonify
from config import Config
from app.middleware.auth import require_admin
from app.services.media_upload_service import upload_to_folder
from app.utils.exceptions import MediaUploadError
from app.utils.cloudinary_helper import extract_public_id_from_url

# Set up logging
logger = logging.getLogger(__name__)

media_bp = Blueprint("media", __name__)


@media_bp.route("/api/admin/media/upload", methods=["POST"])
@require_admin
def upload_media():
    """
    Admin media upload endpoint.
    Accepts multipart/form-data with fields:
      - file: The file to be uploaded (required)
      - folder: The target folder whitelist path (optional, defaults to 'galxy/general')

    Returns:
      JSON: Success or Failure payload.
    """
    # 1. Ensure file is present in multipart request
    if "file" not in request.files:
        logger.error("Upload route called but 'file' parameter was missing.")
        return jsonify({
            "success": False,
            "message": "No file was uploaded or file field is missing.",
            "errors": ["The 'file' parameter must be provided in multipart/form-data."]
        }), 400

    file = request.files["file"]

    # 2. Get the target folder (default if not specified)
    folder = request.form.get("folder", Config.DEFAULT_FOLDER)

    try:
        # 3. Call the media upload service
        url = upload_to_folder(file, folder)

        # 4. Extract public ID from the URL
        public_id = extract_public_id_from_url(url)

        # 5. Return success response
        return jsonify({
            "success": True,
            "data": {
                "url": url,
                "public_id": public_id
            }
        }), 200

    except MediaUploadError as e:
        # Domain exceptions mapped to their specific status codes (e.g. 400, 413, 500)
        logger.warning(f"Business validation error: {e.message}")
        return jsonify({
            "success": False,
            "message": e.message,
            "errors": [e.__class__.__name__]
        }), e.status_code

    except Exception as e:
        # Unexpected server errors (500)
        logger.exception("Unexpected server error occurred during upload.")
        return jsonify({
            "success": False,
            "message": "An unexpected server error occurred.",
            "errors": [str(e)]
        }), 500
