from datetime import datetime
from bson import ObjectId
import pymongo
from app.db import get_db
from app.utils.slug_helper import generate_unique_slug
from app.utils.schema_validator import validate_accent_color, validate_attribute_schema, ACCENT_COLOR_MAP

def serialize_doc(doc):
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    for key, val in doc.items():
        if isinstance(val, datetime):
            doc[key] = val.isoformat()
    return doc

PUBLIC_LIST_FIELDS = {"_id", "slug", "name", "description", "short_tagline", "cover_image", "banner_image", "accent_color", "display_order", "is_active"}

def serialize_public_list(doc):
    if not doc:
        return None
    serialized = serialize_doc(doc)
    return {k: v for k, v in serialized.items() if k in PUBLIC_LIST_FIELDS}

class CategoryService:
    @staticmethod
    def create_category(data):
        db = get_db()
        name = data.get("name")
        if not name:
            raise ValueError("Category name is required")

        accent_color = data.get("accent_color", "neon_pink")
        validate_accent_color(accent_color)

        attribute_schema = data.get("attribute_schema", [])
        if attribute_schema:
            validate_attribute_schema(attribute_schema)
            attribute_schema = sorted(attribute_schema, key=lambda x: x.get("display_order", 0))
        else:
            attribute_schema = []

        slug = generate_unique_slug(name, db.categories)

        category_doc = {
            "slug": slug,
            "name": name,
            "description": data.get("description", ""),
            "short_tagline": data.get("short_tagline", ""),
            "cover_image": data.get("cover_image", ""),
            "banner_image": data.get("banner_image", ""),
            "accent_color": accent_color,
            "display_order": int(data.get("display_order", 0)),
            "is_active": bool(data.get("is_active", True)),
            "ai_prompt_template": data.get("ai_prompt_template", ""),
            "seo": data.get("seo", {}),
            "attribute_schema": attribute_schema,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = db.categories.insert_one(category_doc)
        category_doc["_id"] = result.inserted_id
        return serialize_doc(category_doc)

    @staticmethod
    def update_category(category_id, data):
        db = get_db()
        try:
            obj_id = ObjectId(category_id)
        except Exception:
            raise ValueError("Invalid category ID format")

        existing = db.categories.find_one({"_id": obj_id})
        if not existing:
            return None

        if "slug" in data:
            del data["slug"]
        if "created_at" in data:
            del data["created_at"]
        if "attribute_schema" in data:
            del data["attribute_schema"]

        update_doc = {}
        for field in ["name", "description", "short_tagline", "cover_image", "banner_image",
                      "accent_color", "ai_prompt_template", "seo"]:
            if field in data:
                val = data[field]
                if field == "accent_color":
                    validate_accent_color(val)
                update_doc[field] = val

        if "display_order" in data:
            update_doc["display_order"] = int(data["display_order"])
        if "is_active" in data:
            update_doc["is_active"] = bool(data["is_active"])

        if not update_doc:
            return serialize_doc(existing)

        update_doc["updated_at"] = datetime.utcnow()

        db.categories.update_one({"_id": obj_id}, {"$set": update_doc})
        updated = db.categories.find_one({"_id": obj_id})
        return serialize_doc(updated)

    @staticmethod
    def fetch_all(active_only=False):
        db = get_db()
        query = {}
        if active_only:
            query["is_active"] = True

        cursor = db.categories.find(query).sort("display_order", pymongo.ASCENDING)
        categories = []
        for doc in cursor:
            if active_only:
                categories.append(serialize_public_list(doc))
            else:
                categories.append(serialize_doc(doc))
        return categories

    @staticmethod
    def fetch_by_slug(slug, active_only=False):
        db = get_db()
        query = {"slug": slug}
        if active_only:
            query["is_active"] = True

        doc = db.categories.find_one(query)
        if not doc:
            return None

        result = serialize_doc(doc)
        if active_only:
            result.pop("ai_prompt_template", None)
            schema = result.get("attribute_schema", [])
            if isinstance(schema, list):
                result["attribute_schema"] = sorted(schema, key=lambda x: x.get("display_order", 0))
        return result

    @staticmethod
    def soft_delete(category_id):
        db = get_db()
        try:
            obj_id = ObjectId(category_id)
        except Exception:
            raise ValueError("Invalid category ID format")
            
        # Verify category exists
        existing = db.categories.find_one({"_id": obj_id})
        if not existing:
            return False, "Category not found"
            
        # Check whether active products still reference the category
        product_query = {
            "is_active": True,
            "$or": [
                {"category_id": obj_id},
                {"category_id": str(obj_id)}
            ]
        }
        referencing_product = db.products.find_one(product_query)
        if referencing_product:
            return False, "Cannot delete category: active products still reference it"
            
        # Mark is_active = false
        db.categories.update_one({"_id": obj_id}, {"$set": {"is_active": False, "updated_at": datetime.utcnow()}})
        return True, "Category soft deleted successfully"

    @staticmethod
    def update_attribute_schema(category_id, schema):
        db = get_db()
        try:
            obj_id = ObjectId(category_id)
        except Exception:
            raise ValueError("Invalid category ID format")

        existing = db.categories.find_one({"_id": obj_id})
        if not existing:
            return None

        validate_attribute_schema(schema)
        schema = sorted(schema, key=lambda x: x.get("display_order", 0))

        db.categories.update_one(
            {"_id": obj_id},
            {"$set": {"attribute_schema": schema, "updated_at": datetime.utcnow()}}
        )
        updated = db.categories.find_one({"_id": obj_id})
        return serialize_doc(updated)

    @staticmethod
    def reorder_categories(reorder_data):
        db = get_db()
        if not isinstance(reorder_data, list):
            raise ValueError("Reorder data must be a list")

        for item in reorder_data:
            if not isinstance(item, dict):
                continue
            cat_id = item.get("category_id") or item.get("id")
            order = item.get("display_order")
            if not cat_id or order is None:
                continue

            try:
                obj_id = ObjectId(cat_id)
            except Exception:
                continue

            db.categories.update_one(
                {"_id": obj_id},
                {"$set": {"display_order": int(order), "updated_at": datetime.utcnow()}}
            )
        return True
