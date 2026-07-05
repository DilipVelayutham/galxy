import time
from bson import ObjectId
import app
from app.services.module4_stub import validate_attributes
from app.services.ai_rate_limit_service import check_rate_limit
from app.services.ai_cache_service import check_cache
from app.services.prompt_builder_service import build_prompt
from app.services.ai_provider_client import generate_image
from app.utils.cloudinary_helper import upload_to_cloudinary
from app.models.ai_generation import AIGeneration

def orchestrate_generation(category_id, product_id, selected_attributes, session_id, user_id, input_reference_image=None):
    # Normalize selected_attributes keys alphabetically for deterministic DB matching
    if isinstance(selected_attributes, dict):
        selected_attributes = {k: selected_attributes[k] for k in sorted(selected_attributes.keys())}
        
    # 1. Fetch category from DB
    try:
        cat_obj_id = ObjectId(category_id)
    except Exception as exc:
        return {
            "success": False,
            "status_code": 400,
            "message": "Invalid category_id format"
        }
        
    category = app.db["categories"].find_one({"_id": cat_obj_id})
    if not category:
        return {
            "success": False,
            "status_code": 400,
            "message": f"Category '{category_id}' not found."
        }
        
    # 2. Validation using Module 4's validator stub
    val_res = validate_attributes(category, selected_attributes)
    if not val_res.get("valid"):
        return {
            "success": False,
            "status_code": 400,
            "message": "Validation failed",
            "errors": val_res.get("errors")
        }
        
    # 3. Rate Limit Check
    limit_res = check_rate_limit(user_id, session_id)
    if not limit_res.get("allowed"):
        # Log rate_limited status row
        AIGeneration.insert(
            user_id=user_id,
            session_id=session_id,
            category_id=category_id,
            product_id=product_id,
            selected_attributes=selected_attributes,
            prompt_used="",
            input_reference_image=input_reference_image,
            output_image_url="",
            provider="gemini",
            status="rate_limited",
            error_message="Rate limit exceeded",
            generation_time_ms=0
        )
        return {
            "success": False,
            "status_code": 429,
            "message": "Rate limit exceeded. Please sign up to keep designing.",
            "data": {
                "limit_reached": True,
                "limit_scope": limit_res.get("limit_scope")
            }
        }
        
    # 4. Cache Lookup
    cache_res = check_cache(category_id, selected_attributes)
    if cache_res.get("hit"):
        cached_url = cache_res.get("output_image_url")
        prompt = build_prompt(category, selected_attributes)
        
        # Log successful cache hit row with generation_time_ms: 0
        rec = AIGeneration.insert(
            user_id=user_id,
            session_id=session_id,
            category_id=category_id,
            product_id=product_id,
            selected_attributes=selected_attributes,
            prompt_used=prompt,
            input_reference_image=input_reference_image,
            output_image_url=cached_url,
            provider="gemini",
            status="success",
            error_message=None,
            generation_time_ms=0
        )
        return {
            "success": True,
            "status_code": 200,
            "data": {
                "output_image_url": cached_url,
                "from_cache": True,
                "generation_id": str(rec["_id"]),
                "disclaimer": "AI-generated approximation — final product may vary."
            }
        }
        
    # 5. Prompt Generation
    prompt = build_prompt(category, selected_attributes)
    
    # 6. Provider Call
    start_time = time.time()
    prov_res = generate_image(prompt, input_reference_image=input_reference_image)
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    if not prov_res.get("success"):
        error_msg = prov_res.get("error", "Unknown provider error")
        AIGeneration.insert(
            user_id=user_id,
            session_id=session_id,
            category_id=category_id,
            product_id=product_id,
            selected_attributes=selected_attributes,
            prompt_used=prompt,
            input_reference_image=input_reference_image,
            output_image_url="",
            provider="gemini",
            status="failed",
            error_message=error_msg,
            generation_time_ms=elapsed_ms
        )
        
        # Timeout error maps to 504; standard API failure maps to 502
        status_code = 504 if "timeout" in error_msg.lower() else 502
        return {
            "success": False,
            "status_code": status_code,
            "message": "AI generation service is temporarily unavailable."
        }
        
    # 7. Asset Delivery
    image_bytes = prov_res.get("image_bytes")
    cloudinary_url = upload_to_cloudinary(image_bytes, folder="galxy/ai-previews/")
    
    # 8. Save success row
    rec = AIGeneration.insert(
        user_id=user_id,
        session_id=session_id,
        category_id=category_id,
        product_id=product_id,
        selected_attributes=selected_attributes,
        prompt_used=prompt,
        input_reference_image=input_reference_image,
        output_image_url=cloudinary_url,
        provider="gemini",
        status="success",
        error_message=None,
        generation_time_ms=elapsed_ms
    )
    
    return {
        "success": True,
        "status_code": 200,
        "data": {
            "output_image_url": cloudinary_url,
            "from_cache": False,
            "generation_id": str(rec["_id"]),
            "disclaimer": "AI-generated approximation — final product may vary."
        }
    }
