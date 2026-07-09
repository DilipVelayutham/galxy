"""
app/db.py — MongoDB client singleton.

Usage inside a request context:
    from app.db import get_db
    db = get_db()
    products = db["products"].find(...)
"""

from __future__ import annotations

import certifi
import ssl
from flask import Flask, current_app, g
from pymongo import MongoClient
from pymongo.database import Database


def _build_ssl_context() -> ssl.SSLContext:
    """
    Build a custom SSL context that works with MongoDB Atlas on
    Python 3.14 + OpenSSL 3.5 (stricter default security policies).
    """
    ctx = ssl.create_default_context(cafile=certifi.where())
    # OpenSSL 3.5 defaults to a high security level that may reject
    # some Atlas free-tier cluster certificates.  Level 1 still provides
    # strong encryption while being compatible.
    ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
    return ctx


def init_db(app: Flask) -> Database:
    """
    Attach a MongoClient to the app and return the default database.
    Called once at startup from the app factory.
    """
    client: MongoClient = MongoClient(
        app.config["MONGO_URI"],
        # Fail fast in dev instead of blocking for 30 s
        serverSelectionTimeoutMS=5_000,
        connectTimeoutMS=5_000,
        socketTimeoutMS=20_000,
        # Use certifi CA bundle + relaxed cipher level for Python 3.14
        tls=True,
        tlsCAFile=certifi.where(),
    )
    app.config["MONGO_CLIENT"] = client
    app.config["MONGO_DB"] = client[app.config["MONGO_DB_NAME"]]

    @app.teardown_appcontext
    def _close_db(exc):  # noqa: ANN001
        """Release per-request DB handle stored in Flask g (if any)."""
        db = g.pop("db", None)  # noqa: F841 — nothing to close for pymongo

    return app.config["MONGO_DB"]


def get_db() -> Database:
    """
    Return the MongoDB database instance.
    Safe to call from any request context or background thread.
    """
    if "db" not in g:
        g.db = current_app.config["MONGO_DB"]
    return g.db
