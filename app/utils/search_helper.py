"""
app/utils/search_helper.py — MongoDB query builder for product filtering,
full-text search, and sort specifications.

Owned by: Module 3
"""

from __future__ import annotations

from typing import Any, Optional

from pymongo import ASCENDING, DESCENDING

# ── Filter query builder ───────────────────────────────────────────────────────

def build_filter_query(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    tags: Optional[list[str]] = None,
    featured: Optional[bool] = None,
) -> dict[str, Any]:
    """
    Build a MongoDB filter dict for the products collection.

    All parameters are optional; only provided values are included.
    The query always enforces ``is_active: true``.

    Parameters
    ----------
    category:
        Match products by ``category_slug`` (exact string).
    min_price / max_price:
        Inclusive price range on ``base_price``.
    tags:
        List of tag strings.  Matches products that have **any** of the
        supplied tags (``$in`` semantics).
    featured:
        When True, restrict to ``is_featured: true`` products only.
    """
    query: dict[str, Any] = {"is_active": True}

    if category:
        query["category_slug"] = category

    price_filter: dict[str, float] = {}
    if min_price is not None:
        price_filter["$gte"] = min_price
    if max_price is not None:
        price_filter["$lte"] = max_price
    if price_filter:
        query["base_price"] = price_filter

    if tags:
        query["tags"] = {"$in": tags}

    if featured is True:
        query["is_featured"] = True

    return query


def build_sort_spec(sort_param: Optional[str]) -> list[tuple[str, int]]:
    """
    Map a sort query-param string to a pymongo sort list.

    Supported values
    ----------------
    - ``newest``     (default) — descending ``created_at``
    - ``price_asc``            — ascending  ``base_price``
    - ``price_desc``           — descending ``base_price``
    - ``popular``              — descending ``views``

    Any unrecognised value falls back to ``newest``.
    """
    _map: dict[str, list[tuple[str, int]]] = {
        "newest":     [("created_at", DESCENDING)],
        "price_asc":  [("base_price", ASCENDING)],
        "price_desc": [("base_price", DESCENDING)],
        "popular":    [("views", DESCENDING)],
    }
    return _map.get(sort_param or "newest", [("created_at", DESCENDING)])


def build_text_search_query(q: str) -> dict[str, Any]:
    """
    Build a MongoDB ``$text`` search query dict.

    The products collection must have a text index on ``title`` +
    ``description`` + ``tags`` for this to work (created by
    ``app.models.product.create_indexes``).

    Always enforces ``is_active: true``.
    """
    return {
        "$text": {"$search": q},
        "is_active": True,
    }


# ── Pagination helper ────────────────────────────────────────────────────────

def calc_pagination(page: int, limit: int, total: int) -> dict[str, int]:
    """
    Return a pagination metadata dict.

    Parameters
    ----------
    page:   1-based current page number (clamped to ≥ 1).
    limit:  Documents per page (clamped to ≥ 1).
    total:  Total matching documents.
    """
    import math

    page = max(1, page)
    limit = max(1, limit)
    total_pages = math.ceil(total / limit) if total > 0 else 0

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
    }
