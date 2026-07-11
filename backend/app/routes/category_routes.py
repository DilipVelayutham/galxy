from flask import Blueprint, request, jsonify
from app.services.category_service import CategoryService
from app.middleware.auth import require_admin

category_bp = Blueprint("category_routes", __name__)

# --- Public Endpoints ---

@category_bp.route("/api/categories", methods=["GET"])
def get_categories():
    try:
        categories = CategoryService.fetch_all(active_only=True)
        return jsonify({
            "success": True,
            "data": categories
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@category_bp.route("/api/categories/<slug>", methods=["GET"])
def get_category_by_slug(slug):
    try:
        category = CategoryService.fetch_by_slug(slug, active_only=True)
        if not category:
            return jsonify({
                "success": False,
                "message": f"Category with slug '{slug}' not found"
            }), 404
        return jsonify({
            "success": True,
            "data": category
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# --- Admin Endpoints (Require require_admin) ---

@category_bp.route("/api/admin/categories", methods=["GET"])
@require_admin
def get_admin_categories():
    try:
        categories = CategoryService.fetch_all(active_only=False)
        return jsonify({
            "success": True,
            "data": categories
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@category_bp.route("/api/admin/categories", methods=["POST"])
@require_admin
def create_category():
    try:
        data = request.get_json() or {}
        category = CategoryService.create_category(data)
        return jsonify({
            "success": True,
            "message": "Category created successfully",
            "data": category
        }), 201
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@category_bp.route("/api/admin/categories/<id>", methods=["PUT"])
@require_admin
def update_category(id):
    try:
        data = request.get_json() or {}
        category = CategoryService.update_category(id, data)
        if not category:
            return jsonify({
                "success": False,
                "message": "Category not found"
            }), 404
        return jsonify({
            "success": True,
            "message": "Category updated successfully",
            "data": category
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@category_bp.route("/api/admin/categories/<id>", methods=["DELETE"])
@require_admin
def delete_category(id):
    try:
        success, message = CategoryService.soft_delete(id)
        if not success:
            if "not found" in message.lower():
                return jsonify({
                    "success": False,
                    "message": message
                }), 404
            else:
                # Return 409 Conflict if active products still reference it (Step 6)
                return jsonify({
                    "success": False,
                    "message": message
                }), 409
        return jsonify({
            "success": True,
            "message": message
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@category_bp.route("/api/admin/categories/reorder", methods=["PUT"])
@require_admin
def reorder_categories():
    try:
        data = request.get_json() or {}
        order_list = data.get("order", data) if isinstance(data, dict) else data
        if not isinstance(order_list, list):
            raise ValueError("Request must contain an 'order' array with {category_id, display_order} objects")

        CategoryService.reorder_categories(order_list)
        return jsonify({
            "success": True,
            "message": "Categories reordered successfully"
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@category_bp.route("/api/admin/categories/<id>/attribute-schema", methods=["PUT"])
@require_admin
def update_attribute_schema(id):
    try:
        data = request.get_json() or {}
        schema = data
        if isinstance(data, dict) and "attribute_schema" in data:
            schema = data["attribute_schema"]

        if not isinstance(schema, list):
            return jsonify({
                "success": False,
                "message": "Attribute schema must be a list"
            }), 400

        category = CategoryService.update_attribute_schema(id, schema)
        if not category:
            return jsonify({
                "success": False,
                "message": "Category not found"
            }), 404
        return jsonify({
            "success": True,
            "message": "Attribute schema updated successfully",
            "data": category
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

