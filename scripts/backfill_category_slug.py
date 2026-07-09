"""
scripts/backfill_category_slug.py
----------------------------------
Backfill the denormalized ``category_slug`` field on all product documents
after a category slug has been renamed.

# FLAG: Module 2 dependency
# ──────────────────────────────────────────────────────────────────────────────
# category_slug is a denormalized copy of the category's slug field.
# If Module 2 renames a category slug, this script MUST be run against the
# products collection to keep the denormalized field in sync.
#
# Module 2 team: please notify Module 3 whenever a category slug changes so
# this backfill can be coordinated.
# ──────────────────────────────────────────────────────────────────────────────

Usage
-----
    # From the project root:
    python scripts/backfill_category_slug.py \\
        --old-slug neon-boards \\
        --new-slug neon-name-boards

    # Dry run (prints what would change, no writes):
    python scripts/backfill_category_slug.py \\
        --old-slug neon-boards \\
        --new-slug neon-name-boards \\
        --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env so the default --mongo-uri points to Atlas, not localhost
load_dotenv()

# ── CLI ────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backfill category_slug on products after a category rename."
    )
    parser.add_argument("--old-slug", required=True, help="The old category slug to replace.")
    parser.add_argument("--new-slug", required=True, help="The new category slug to write.")
    parser.add_argument(
        "--mongo-uri",
        default=os.environ.get("MONGO_URI", "mongodb://localhost:27017"),
        help="MongoDB connection URI (default: reads MONGO_URI from .env).",
    )
    parser.add_argument(
        "--db-name",
        default=os.environ.get("MONGO_DB_NAME", "galaxy_pro"),
        help="MongoDB database name (default: reads MONGO_DB_NAME from .env).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing anything.",
    )
    return parser.parse_args()


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    print(f"Connecting to {args.mongo_uri} / {args.db_name} …")
    client = MongoClient(args.mongo_uri)
    db = client[args.db_name]
    col = db["products"]

    filter_query = {"category_slug": args.old_slug}
    affected = col.count_documents(filter_query)

    if affected == 0:
        print(f"No products found with category_slug='{args.old_slug}'. Nothing to do.")
        sys.exit(0)

    print(f"Found {affected} product(s) with category_slug='{args.old_slug}'.")

    if args.dry_run:
        print("[DRY RUN] Would update:")
        for doc in col.find(filter_query, {"_id": 1, "slug": 1, "title": 1}):
            print(f"  • {doc['slug']} (id={doc['_id']})")
        print("[DRY RUN] No changes written.")
        sys.exit(0)

    # Confirm before writing
    confirm = input(
        f"\nAbout to update {affected} document(s): "
        f"category_slug '{args.old_slug}' → '{args.new_slug}'.\n"
        "Type 'yes' to proceed: "
    ).strip().lower()

    if confirm != "yes":
        print("Aborted.")
        sys.exit(1)

    result = col.update_many(
        filter_query,
        {
            "$set": {
                "category_slug": args.new_slug,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    print(f"Done. {result.modified_count} product(s) updated.")


if __name__ == "__main__":
    main()
