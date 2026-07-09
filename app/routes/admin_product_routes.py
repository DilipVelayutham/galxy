import logging
from flask import Blueprint, request
from app.utils.auth_helper import require_admin
from app.utils.response_helper import success_response, paginated_response, error_response
from app.utils.validators.product_validator import validate_product_data
from app.services.product_service import ProductService
from app.services.product_image_service import ProductImageService

logger = logging.getLogger(__name__)

admin_product_bp = Blueprint("admin_products", __name__)

@admin_product_bp.route("", methods=["GET"])
@require_admin
def get_admin_products():
    """
    Admin catalog list endpoint.
    Retrieves all products including inactive and out-of-stock items.
    Query parameters can include category, stock_status, is_active, page, limit.
    """
    try:
        params = request.args
        products, page, limit, total = ProductService.get_products(params, include_inactive=True)
        return paginated_response(products, page, limit, total)
    except Exception as e:
        logger.error(f"Admin fetch products list failed: {e}")
        return error_response(f"Failed to fetch products: {str(e)}", status_code=500)

@admin_product_bp.route("", methods=["POST"])
@require_admin
def create_product():
    """
    Admin create product endpoint.
    Body:
        { "category_id", "title", "type", "base_price", "description", "specifications", 
          "default_attributes", "stock_status", "tags", "is_featured" }
    Validates data, checks default_attributes against category's attribute_schema, 
    and inserts product.
    """
    try:
        data = request.get_json() or {}
        errors, warning, validated_data = validate_product_data(data, is_update=False)
        
        if errors:
            return error_response(
                message="Validation failed for product creation.",
                errors=errors,
                status_code=400
            )
            
        product = ProductService.create_product(validated_data)
        
        msg = "Product created successfully."
        if warning:
            msg += f" {warning}"
            
        return success_response(product, message=msg, status_code=201)
    except Exception as e:
        logger.error(f"Admin product creation failed: {e}")
        return error_response(f"Product creation failed: {str(e)}", status_code=500)

@admin_product_bp.route("/<id>", methods=["PUT"])
@require_admin
def update_product(id):
    """
    Admin update product endpoint.
    Accepts any subset of fields except slug and category_id.
    Validates data and updates.
    """
    try:
        data = request.get_json() or {}
        
        # Disallow updating category_id or category_slug
        if "category_id" in data or "category_slug" in data:
            return error_response(
                message="Invalid operation.",
                errors={"category_id": "Changing category_id or category_slug after creation is disallowed."},
                status_code=400
            )
            
        errors, warning, validated_data = validate_product_data(data, is_update=True, product_id=id)
        
        if errors:
            return error_response(
                message="Validation failed for product update.",
                errors=errors,
                status_code=400
            )
            
        product = ProductService.update_product(id, validated_data)
        if not product:
            return error_response("Product not found.", status_code=404)
            
        msg = "Product updated successfully."
        if warning:
            msg += f" {warning}"
            
        return success_response(product, message=msg)
    except ValueError as ve:
        return error_response(str(ve), status_code=400)
    except Exception as e:
        logger.error(f"Admin product update failed for {id}: {e}")
        return error_response(f"Product update failed: {str(e)}", status_code=500)

@admin_product_bp.route("/<id>", methods=["DELETE"])
@require_admin
def delete_product(id):
    """
    Admin soft-delete product endpoint.
    Sets is_active to False.
    """
    try:
        product = ProductService.soft_delete_product(id)
        if not product:
            return error_response("Product not found.", status_code=404)
        return success_response(product, message="Product soft-deleted successfully.")
    except ValueError as ve:
        return error_response(str(ve), status_code=400)
    except Exception as e:
        logger.error(f"Admin product deletion failed for {id}: {e}")
        return error_response(f"Product deletion failed: {str(e)}", status_code=500)

@admin_product_bp.route("/<id>/images", methods=["POST"])
@require_admin
def upload_product_images(id):
    """
    Admin image upload endpoint.
    Multipart form data, expects one or more files in 'images' field.
    """
    try:
        if 'images' not in request.files:
            return error_response(
                message="Missing file upload parameter.",
                errors={"images": "Field 'images' containing files is required."},
                status_code=400
            )
            
        files = request.files.getlist("images")
        if not files or files[0].filename == '':
            return error_response(
                message="No files selected.",
                errors={"images": "At least one file must be selected for upload."},
                status_code=400
            )
            
        result = ProductImageService.upload_images(id, files)
        if not result:
            return error_response("Product not found.", status_code=404)
            
        return success_response(result, message="Images uploaded successfully.")
    except ValueError as ve:
        return error_response(str(ve), status_code=400)
    except Exception as e:
        logger.error(f"Admin image upload failed for product {id}: {e}")
        return error_response(f"Image upload failed: {str(e)}", status_code=500)

@admin_product_bp.route("/<id>/images", methods=["DELETE"])
@require_admin
def delete_product_image(id):
    """
    Admin delete image endpoint.
    Body: { "image_url" }
    Removes image from product array and deletes from Cloudinary.
    Resets thumbnail if it matches the deleted URL.
    """
    try:
        data = request.get_json() or {}
        image_url = data.get("image_url")
        
        if not image_url:
            return error_response(
                message="Missing required field.",
                errors={"image_url": "image_url is required in request body."},
                status_code=400
            )
            
        result = ProductImageService.delete_image(id, image_url)
        if not result:
            return error_response("Product not found.", status_code=404)
            
        return success_response(result, message="Image deleted successfully.")
    except ValueError as ve:
        return error_response(str(ve), status_code=400)
    except Exception as e:
        logger.error(f"Admin image deletion failed for product {id}: {e}")
        return error_response(f"Image deletion failed: {str(e)}", status_code=500)

@admin_product_bp.route("/<id>/thumbnail", methods=["PUT"])
@require_admin
def update_product_thumbnail(id):
    """
    Admin update thumbnail endpoint.
    Body: { "image_url" }
    Ensures image_url is in the product's image collection, then sets it as thumbnail.
    """
    try:
        data = request.get_json() or {}
        image_url = data.get("image_url")
        
        if not image_url:
            return error_response(
                message="Missing required field.",
                errors={"image_url": "image_url is required in request body."},
                status_code=400
            )
            
        product = ProductService.set_thumbnail(id, image_url)
        if not product:
            return error_response("Product not found.", status_code=404)
            
        return success_response(product, message="Product thumbnail updated successfully.")
    except ValueError as ve:
        return error_response(str(ve), status_code=400)
    except Exception as e:
        logger.error(f"Admin thumbnail update failed for product {id}: {e}")
        return error_response(f"Thumbnail update failed: {str(e)}", status_code=500)
