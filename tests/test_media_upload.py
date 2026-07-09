import io
import socket
from unittest.mock import patch, MagicMock
from config import Config

# A valid 1x1 pixel PNG image bytes to pass Pillow verification
VALID_PNG_BYTES = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82'


@patch("cloudinary.uploader.upload")
def test_upload_success(mock_upload, client, admin_headers):
    """Test successful image upload with valid parameters and admin auth."""
    mock_upload.return_value = {
        "secure_url": "https://res.cloudinary.com/test_cloud/image/upload/v123456789/galxy/products/image.png",
        "public_id": "galxy/products/image",
        "width": 100,
        "height": 100,
        "format": "png"
    }

    data = {
        "file": (io.BytesIO(VALID_PNG_BYTES), "test.png"),
        "folder": "galxy/products"
    }
    response = client.post(
        "/api/admin/media/upload",
        headers=admin_headers,
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 200
    res_json = response.get_json()
    assert res_json["success"] is True
    assert res_json["data"]["url"] == "https://res.cloudinary.com/test_cloud/image/upload/v123456789/galxy/products/image.png"
    assert res_json["data"]["public_id"] == "galxy/products/image"
    mock_upload.assert_called_once()


@patch("cloudinary.uploader.upload")
def test_upload_success_is_admin_claim(mock_upload, client, admin_secret_headers):
    """Test successful image upload using JWT with is_admin claim."""
    mock_upload.return_value = {
        "secure_url": "https://res.cloudinary.com/test_cloud/image/upload/v123456789/galxy/general/image.png",
        "public_id": "galxy/general/image",
        "width": 100,
        "height": 100,
        "format": "png"
    }

    data = {
        "file": (io.BytesIO(VALID_PNG_BYTES), "test.png")
    }
    response = client.post(
        "/api/admin/media/upload",
        headers=admin_secret_headers,
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 200
    res_json = response.get_json()
    assert res_json["success"] is True
    assert res_json["data"]["url"] == "https://res.cloudinary.com/test_cloud/image/upload/v123456789/galxy/general/image.png"
    assert res_json["data"]["public_id"] == "galxy/general/image"
    mock_upload.assert_called_once()


def test_upload_missing_file(client, admin_headers):
    """Test response when the file payload is missing."""
    data = {
        "folder": "galxy/products"
    }
    response = client.post(
        "/api/admin/media/upload",
        headers=admin_headers,
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 400
    res_json = response.get_json()
    assert res_json["success"] is False
    assert "No file was uploaded" in res_json["message"]


def test_upload_invalid_extension(client, admin_headers):
    """Test upload rejection for disallowed file extensions."""
    data = {
        "file": (io.BytesIO(b"fake text data"), "test.txt"),
        "folder": "galxy/products"
    }
    response = client.post(
        "/api/admin/media/upload",
        headers=admin_headers,
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 400
    res_json = response.get_json()
    assert res_json["success"] is False
    assert "Unsupported file extension" in res_json["message"]


def test_upload_invalid_mime_type(client, admin_headers):
    """Test upload rejection for invalid MIME content type."""
    data = {
        "file": (io.BytesIO(VALID_PNG_BYTES), "test.png"),
        "folder": "galxy/products"
    }
    # Set an invalid MIME type like text/plain for test.png
    response = client.post(
        "/api/admin/media/upload",
        headers=admin_headers,
        data=data,
        content_type="multipart/form-data"
    )
    # Define content type for the file:
    data = {
        "file": (io.BytesIO(VALID_PNG_BYTES), "test.png", "text/plain"),
        "folder": "galxy/products"
    }
    response = client.post(
        "/api/admin/media/upload",
        headers=admin_headers,
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 400
    res_json = response.get_json()
    assert res_json["success"] is False
    assert "Unsupported MIME type" in res_json["message"]


def test_upload_file_too_large(client, admin_headers):
    """Test file size limit validation."""
    # Build content exceeding MAX_FILE_SIZE_BYTES (5MB)
    large_data = b"0" * (Config.MAX_FILE_SIZE_BYTES + 1024)
    data = {
        "file": (io.BytesIO(large_data), "test.png", "image/png"),
        "folder": "galxy/products"
    }
    response = client.post(
        "/api/admin/media/upload",
        headers=admin_headers,
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 413
    res_json = response.get_json()
    assert res_json["success"] is False
    assert "exceeds" in res_json["message"]


def test_upload_invalid_folder_name(client, admin_headers):
    """Test target folder validation against whitelist."""
    data = {
        "file": (io.BytesIO(VALID_PNG_BYTES), "test.png", "image/png"),
        "folder": "galxy/unauthorized-folder"
    }
    response = client.post(
        "/api/admin/media/upload",
        headers=admin_headers,
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 400
    res_json = response.get_json()
    assert res_json["success"] is False
    assert "is not allowed" in res_json["message"]


@patch("cloudinary.uploader.upload")
def test_cloudinary_upload_failure(mock_upload, client, admin_headers):
    """Test error handling when Cloudinary API consistently fails."""
    mock_upload.side_effect = Exception("Cloudinary connection timed out")

    data = {
        "file": (io.BytesIO(VALID_PNG_BYTES), "test.png", "image/png"),
        "folder": "galxy/products"
    }
    with patch("time.sleep"):
        response = client.post(
            "/api/admin/media/upload",
            headers=admin_headers,
            data=data,
            content_type="multipart/form-data"
        )

    assert response.status_code == 500
    res_json = response.get_json()
    assert res_json["success"] is False
    assert "Cloudinary upload service failed" in res_json["message"]
    # Should have run all 4 attempts (1 initial + 3 retries)
    assert mock_upload.call_count == 4


@patch("cloudinary.uploader.upload")
def test_cloudinary_upload_success_after_retries(mock_upload, client, admin_headers):
    """Test success after retrying a failed attempt."""
    mock_upload.side_effect = [
        Exception("Timeout"),
        Exception("Temporary Service Failure"),
        {
            "secure_url": "https://res.cloudinary.com/test_cloud/image/upload/v123456789/galxy/products/image.png",
            "public_id": "galxy/products/image",
            "width": 100,
            "height": 100,
            "format": "png"
        }
    ]

    data = {
        "file": (io.BytesIO(VALID_PNG_BYTES), "test.png", "image/png"),
        "folder": "galxy/products"
    }
    # Temporarily speed up sleep delay in tests by patching time.sleep
    with patch("time.sleep") as mock_sleep:
        response = client.post(
            "/api/admin/media/upload",
            headers=admin_headers,
            data=data,
            content_type="multipart/form-data"
        )

    assert response.status_code == 200
    res_json = response.get_json()
    assert res_json["success"] is True
    assert res_json["data"]["url"] == "https://res.cloudinary.com/test_cloud/image/upload/v123456789/galxy/products/image.png"
    assert mock_upload.call_count == 3
    assert mock_sleep.call_count == 2


def test_upload_unauthorized_request(client, invalid_auth_headers):
    """Test upload rejection when using an invalid bearer token."""
    data = {
        "file": (io.BytesIO(VALID_PNG_BYTES), "test.png", "image/png"),
        "folder": "galxy/products"
    }
    response = client.post(
        "/api/admin/media/upload",
        headers=invalid_auth_headers,
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 401
    res_json = response.get_json()
    assert res_json["success"] is False
    assert "Unauthorized" in res_json["message"]


def test_upload_missing_authentication(client):
    """Test upload rejection when auth header is missing completely."""
    data = {
        "file": (io.BytesIO(VALID_PNG_BYTES), "test.png", "image/png"),
        "folder": "galxy/products"
    }
    response = client.post(
        "/api/admin/media/upload",
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 401
    res_json = response.get_json()
    assert res_json["success"] is False
    assert "Unauthorized" in res_json["message"]


def test_upload_corrupted_image(client, admin_headers):
    """Test upload rejection when file content is corrupted or not a valid image."""
    data = {
        "file": (io.BytesIO(b"corrupted binary data"), "test.png", "image/png"),
        "folder": "galxy/products"
    }
    response = client.post(
        "/api/admin/media/upload",
        headers=admin_headers,
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    res_json = response.get_json()
    assert res_json["success"] is False
    assert "corrupted" in res_json["message"]


@patch("PIL.Image.open")
def test_upload_invalid_image_dimensions(mock_open, client, admin_headers):
    """Test upload rejection when image dimensions are invalid (e.g. width/height <= 0)."""
    mock_img = MagicMock()
    mock_img.verify.return_value = None
    mock_img.size = (0, 100)  # Invalid width
    mock_img.format = "PNG"
    mock_open.return_value = mock_img

    data = {
        "file": (io.BytesIO(VALID_PNG_BYTES), "test.png", "image/png"),
        "folder": "galxy/products"
    }
    response = client.post(
        "/api/admin/media/upload",
        headers=admin_headers,
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    res_json = response.get_json()
    assert res_json["success"] is False
    assert "dimensions" in res_json["message"]


@patch("cloudinary.uploader.upload")
def test_cloudinary_upload_timeout(mock_upload, client, admin_headers):
    """Test error handling when Cloudinary API times out."""
    mock_upload.side_effect = socket.timeout("Connection timed out")

    data = {
        "file": (io.BytesIO(VALID_PNG_BYTES), "test.png", "image/png"),
        "folder": "galxy/products"
    }
    with patch("time.sleep"):
        response = client.post(
            "/api/admin/media/upload",
            headers=admin_headers,
            data=data,
            content_type="multipart/form-data"
        )

    assert response.status_code == 504
    res_json = response.get_json()
    assert res_json["success"] is False
    assert "timed out" in res_json["message"]
    assert mock_upload.call_count == 4


def test_upload_forbidden_request(client, app):
    """Test upload rejection when using a valid JWT with a non-admin role (403 Forbidden)."""
    import jwt
    import time
    payload = {
        "role": "user",  # Non-admin role
        "exp": int(time.time()) + 3600
    }
    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    data = {
        "file": (io.BytesIO(VALID_PNG_BYTES), "test.png", "image/png"),
        "folder": "galxy/products"
    }
    response = client.post(
        "/api/admin/media/upload",
        headers=headers,
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 403
    res_json = response.get_json()
    assert res_json["success"] is False
    assert "Forbidden" in res_json["message"]
