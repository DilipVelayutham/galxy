import os
import io
import uuid
import cloudinary
import cloudinary.uploader

# Path to local static previews folder (served by Flask)
_STATIC_PREVIEWS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'previews')


def upload_to_cloudinary(image_bytes, folder="galxy/ai-previews/"):
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not (cloud_name and api_key and api_secret):
        # --- LOCAL DEVELOPMENT FALLBACK ---
        # Save the image bytes to /static/previews/ and return a local URL
        # so the browser can actually load the generated preview image.
        os.makedirs(_STATIC_PREVIEWS_DIR, exist_ok=True)
        filename = f"mock-preview-{uuid.uuid4().hex}.png"
        filepath = os.path.join(_STATIC_PREVIEWS_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        return f"/static/previews/{filename}"

    try:
        # --- PRODUCTION: Upload to Cloudinary ---
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        file_io = io.BytesIO(image_bytes)
        result = cloudinary.uploader.upload(
            file_io,
            folder=folder,
            resource_type="image"
        )
        return result.get("secure_url")
    except Exception as e:
        # Propagate the error so a failed upload doesn't result in a fake success URL
        raise Exception(f"Cloudinary upload failed: {str(e)}")
