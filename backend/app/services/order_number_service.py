"""
app/services/order_number_service.py

Atomic, collision-safe order number generation: GLX-{year}-{5-digit seq}.

Uses a `counters` collection with one document per calendar year
({"_id": "order_<year>", "seq": <int>}), incremented via
findOneAndUpdate($inc). Do NOT generate the number by counting existing
orders — that's unsafe under concurrent checkouts and can produce
duplicates. The sequence resets automatically each year since a new
counter document is created (via upsert) the first time that year is seen.
"""

from datetime import datetime, timezone
from typing import Optional

from pymongo import ReturnDocument
from pymongo.database import Database

from app.models.order import COUNTERS_COLLECTION

ORDER_NUMBER_PREFIX = "GLX"
SEQUENCE_WIDTH = 5


def _counter_id_for_year(year: int) -> str:
    return f"order_{year}"


def generate_order_number(db: Database, *, year: Optional[int] = None) -> str:
    """Atomically reserve the next order number for the given year
    (defaults to the current UTC year). Safe under concurrent checkouts —
    the increment is a single findOneAndUpdate round-trip, so two
    simultaneous checkouts can never be handed the same sequence value.
    """
    year = year or datetime.now(timezone.utc).year
    counter_id = _counter_id_for_year(year)

    result = db[COUNTERS_COLLECTION].find_one_and_update(
        {"_id": counter_id},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    sequence = result["seq"]
    return f"{ORDER_NUMBER_PREFIX}-{year}-{str(sequence).zfill(SEQUENCE_WIDTH)}"
