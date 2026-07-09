"""
app/services/product_image_service.py — Cloudinary image upload and deletion.

Owned by: Module 3

Usage
-----
    from app.services.product_image_service import upload_image, delete_image

    # Upload a FileStorage object from Flask's request.files
    url, public_id = upload_image(request.files["image"], folder="products")

    # Delete by public_id
    delete_image(public_id)
"""

from __future__ import annotations

import re
from typing import Optional

import cloudinary
import cloudinary.uploader
from werkzeug.datastructures import FileStorage


# ── Upload ────────────────────────────────────────────────────────────

def upload_image(
    file: FileStorage,
    folder: str = "products",
    *,
    transformation: Optional[dict] = None,
) -> tuple[str, str]:
    """
    Upload a file to Cloudinary and return ``(secure_url, public_id)``.

    Parameters
    ----------
    file:
        A Werkzeug ``FileStorage`` object (from ``request.files``).
    folder:
        Cloudinary folder path. Defaults to ``"products"``.
    transformation:
        Optional Cloudinary eager transformation dict, e.g.
        ``{"width": 800, "crop": "limit", "quality": "auto"}``.

    Returns
    -------
    (secure_url, public_id)

    Raises
    ------
    cloudinary.exceptions.Error
        If the upload fails on the Cloudinary side.
    ValueError
        If ``file`` is None or has no filename.
    """
    if file is None or not file.filename:
        raise ValueError("A valid file must be provided for upload.")

    upload_params: dict = {
        "folder": folder,
        "resource_type": "image",
        "overwrite": False,
        "invalidate": True,
    }

    if transformation:
        upload_params["transformation"] = transformation
    else:
        # Default: sensible quality + format auto-select
        upload_params["transformation"] = [
            {"quality": "auto", "fetch_format": "auto"},
        ]

    result = cloudinary.uploader.upload(file, **upload_params)

    secure_url: str = result.get("secure_url", "")
    public_id: str = result.get("public_id", "")

    return secure_url, public_id


def upload_thumbnail(file: FileStorage, folder: str = "products/thumbnails") -> tuple[str, str]:
    """
    Upload a thumbnail image with a fixed 400×400 crop for consistency.

    Returns ``(secure_url, public_id)``.
    """
    return upload_image(
        file,
        folder=folder,
        transformation=[
            {"width": 400, "height": 400, "crop": "fill", "gravity": "auto"},
            {"quality": "auto", "fetch_format": "auto"},
        ],
    )


# ── Delete ───────────────────────────────────────────────────────────

def delete_image(public_id: str) -> bool:
    """
    Delete an asset from Cloudinary by its ``public_id``.

    Returns True if the deletion was acknowledged, False otherwise.

    Parameters
    ----------
    public_id:
        The Cloudinary public_id (e.g. ``"products/abc123"``).
    """
    if not public_id:
        return False

    result = cloudinary.uploader.destroy(public_id, invalidate=True)
    return result.get("result") == "ok"


# ── URL parsing ──────────────────────────────────────────────────────────

def extract_public_id(cloudinary_url: str) -> Optional[str]:
    """
    Extract the ``public_id`` from a Cloudinary secure URL.

    Cloudinary URLs follow the pattern::

        https://res.cloudinary.com/<cloud_name>/image/upload/[v<version>/]<public_id>.<ext>

    Examples
    --------
    >>> extract_public_id(
    ...     "https://res.cloudinary.com/demo/image/upload/v1234/products/my-sign.jpg"
    ... )
    'products/my-sign'

    Returns None if the URL does not match the expected Cloudinary pattern.
    """
    if not cloudinary_url:
        return None

    # Strip version segment (v<digits>/) if present
    pattern = r"cloudinary\.com/[^/]+/image/upload/(?:v\d+/)?(.+?)(?:\.[a-zA-Z0-9]+)?$"
    match = re.search(pattern, cloudinary_url)
    if match:
        return match.group(1)
    return None
