class MediaUploadError(Exception):
    """Base exception class for media upload utility errors."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class MissingFileError(MediaUploadError):
    """Raised when no file is present in the request."""

    def __init__(self, message: str = "No file was uploaded or file field is missing."):
        super().__init__(message, status_code=400)


class InvalidFolderError(MediaUploadError):
    """Raised when the folder name is not in the whitelist."""

    def __init__(self, folder_name: str, allowed_folders: list[str] | set[str]):
        message = f"Folder '{folder_name}' is not allowed. Whitelist: {', '.join(allowed_folders)}"
        super().__init__(message, status_code=400)


class InvalidExtensionError(MediaUploadError):
    """Raised when the file has an unsupported format/extension."""

    def __init__(self, extension: str, allowed_formats: list[str] | set[str]):
        message = f"Unsupported file extension '{extension}'. Allowed formats: {', '.join(allowed_formats)}"
        super().__init__(message, status_code=400)


class FileSizeExceededError(MediaUploadError):
    """Raised when the file exceeds the maximum allowed size."""

    def __init__(self, size_mb: float, max_size_mb: float = 5.0):
        message = f"File size ({size_mb:.2f} MB) exceeds the maximum limit of {max_size_mb} MB."
        super().__init__(message, status_code=413)


class CloudinaryUploadError(MediaUploadError):
    """Raised when the upload to Cloudinary fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class InvalidMimeTypeError(MediaUploadError):
    """Raised when the file has an unsupported MIME type."""

    def __init__(self, mime_type: str, allowed_mime_types: list[str] | set[str]):
        message = f"Unsupported MIME type '{mime_type}'. Allowed types: {', '.join(allowed_mime_types)}"
        super().__init__(message, status_code=400)


class CloudinaryTimeoutError(MediaUploadError):
    """Raised when the upload to Cloudinary times out."""

    def __init__(self, message: str = "Cloudinary upload service timed out. Please try again."):
        super().__init__(message, status_code=504)


class CorruptedImageError(MediaUploadError):
    """Raised when the uploaded file is corrupted or not a valid image."""

    def __init__(self, message: str = "The uploaded file is corrupted or not a valid image."):
        super().__init__(message, status_code=400)


class InvalidImageDimensionsError(MediaUploadError):
    """Raised when the image dimensions are invalid (e.g. 0 or negative)."""

    def __init__(self, message: str = "Image dimensions must be greater than zero."):
        super().__init__(message, status_code=400)
