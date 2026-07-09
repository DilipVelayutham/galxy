"""
app/utils/slug_helper.py — Slug generation and uniqueness enforcement.

Canonical source for Module 3; Module 2 may import from here or provide
their own identical interface.
"""

from __future__ import annotations

from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection
from slugify import slugify


def generate_slug(text: str) -> str:
    """
    Convert an arbitrary string to a URL-safe slug.

    Examples
    --------
    >>> generate_slug("Custom Cursive Neon Sign!")
    'custom-cursive-neon-sign'
    >>> generate_slug("Café & Co.")
    'cafe-and-co'
    """
    return slugify(text, allow_unicode=False, separator="-")


def ensure_unique_slug(
    base_slug: str,
    collection: Collection,
    exclude_id: Optional[ObjectId] = None,
) -> str:
    """
    Return a slug that is unique within *collection*.

    If *base_slug* already exists in the collection (for a document whose
    ``_id`` is not *exclude_id*), appends an incrementing numeric suffix:
    ``base_slug`` → ``base_slug-2`` → ``base_slug-3`` → …

    Parameters
    ----------
    base_slug:
        The preferred slug derived from the product title.
    collection:
        The PyMongo collection to check for collisions.
    exclude_id:
        When updating an existing document, pass its ``_id`` so the check
        does not collide with itself.
    """
    candidate = base_slug
    counter = 2

    while True:
        query: dict = {"slug": candidate}
        if exclude_id is not None:
            query["_id"] = {"$ne": exclude_id}

        if collection.count_documents(query, limit=1) == 0:
            return candidate

        candidate = f"{base_slug}-{counter}"
        counter += 1
