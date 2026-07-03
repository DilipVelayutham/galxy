import os
import time
import datetime
from bson import ObjectId
import cloudinary.uploader
import cloudinary

from app.database import categories, ai_generations
from app.configs.ai_config import (
    CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET,
    AI_PROVIDER
)
from app.models.ai_generation import AIGeneration
from app.services.module4_service import validate_attributes
from app.services.ai_cache_service import check_cache, store_cache
from app.services.ai_rate_limit_service import check_rate_limit
from app.services.prompt_builder_service import build_prompt
from app.services.ai_provider_client import generate_preview_image

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

def generate_preview(category_id, selected_attributes, user_id=None, session_id=None, product_id=None):
    """
    Orchestrates the entire AI Preview Generation Pipeline:
    1. Validation (Module 4)
    2. Cache check (T3)
    3. Rate limit check (T4)
    4. Prompt compilation (T2)
    5. API Provider call (T2)
    6. Cloudinary upload
    7. Cache storage (T3)
    8. Logging (T1)
    """
    # 1. Fetch category from DB
    try:
        cat_obj_id = ObjectId(category_id) if isinstance(category_id, str) and len(category_id) == 24 else category_id
    except Exception:
        cat_obj_id = category_id
        
    category = categories.find_one({"$or": [{"_id": cat_obj_id}, {"category_id": category_id}]})
    if not category:
        return {
            "success": False,
            "status": 404,
            "message": f"Category '{category_id}' not found."
        }

    # 2. Call Module 4's validation engine
    val_result = validate_attributes(category_id, selected_attributes)
    if not val_result.get("valid"):
        return {
            "success": False,
            "status": 400,
            "message": "Invalid attributes selected.",
            "errors": val_result.get("errors", [])
        }

    # 3. Check Caching tier
    cache_result = check_cache(category_id, selected_attributes)
    if cache_result.get("hit"):
        cached_url = cache_result.get("output_image_url")
        prompt_compiled = build_prompt(category, selected_attributes)
        
        # Log cache hit in DB using AIGeneration model (generation_time_ms = 0)
        try:
            gen_model = AIGeneration(
                user_id=user_id,
                session_id=session_id,
                category_id=category_id,
                product_id=product_id,
                selected_attributes=selected_attributes,
                prompt_used=prompt_compiled,
                output_image_url=cached_url,
                provider=AI_PROVIDER,
                status="success",
                error_message=None,
                generation_time_ms=0
            )
            log_result = ai_generations.insert_one(gen_model.to_dict())
            generation_id = str(log_result.inserted_id)
        except Exception as e:
            print(f"[Orchestrator] Error logging cache hit: {e}")
            generation_id = "cache_hit_unlogged"

        return {
            "success": True,
            "status": 200,
            "data": {
                "output_image_url": cached_url,
                "from_cache": True,
                "generation_id": generation_id,
                "disclaimer": "AI-generated approximation — final product may vary."
            }
        }

    # 4. Check Rate Limiting tier
    rate_result = check_rate_limit(user_id=user_id, session_id=session_id)
    if not rate_result.get("allowed"):
        # Log rate limited state in DB using AIGeneration model
        try:
            gen_model = AIGeneration(
                user_id=user_id,
                session_id=session_id,
                category_id=category_id,
                product_id=product_id,
                selected_attributes=selected_attributes,
                prompt_used="",
                output_image_url="",
                provider=AI_PROVIDER,
                status="rate_limited",
                error_message=f"Rate limit reached for {rate_result.get('limit_scope')}",
                generation_time_ms=0
            )
            ai_generations.insert_one(gen_model.to_dict())
        except Exception as e:
            print(f"[Orchestrator] Error logging rate limit block: {e}")
            
        return {
            "success": False,
            "status": 429,
            "message": "AI generation rate limit reached.",
            "data": {
                "limit_reached": True,
                "limit_scope": rate_result.get("limit_scope")
            }
        }

    # 5. Build prompt
    prompt_compiled = build_prompt(category, selected_attributes)
    
    # 6. Call provider to generate image
    start_time = time.time()
    try:
        image_bytes = generate_preview_image(prompt_compiled)
        generation_time_ms = int((time.time() - start_time) * 1000)
    except Exception as e:
        error_msg = str(e)
        # Log failure in DB using AIGeneration model
        try:
            gen_model = AIGeneration(
                user_id=user_id,
                session_id=session_id,
                category_id=category_id,
                product_id=product_id,
                selected_attributes=selected_attributes,
                prompt_used=prompt_compiled,
                output_image_url="",
                provider=AI_PROVIDER,
                status="failed",
                error_message=error_msg,
                generation_time_ms=int((time.time() - start_time) * 1000)
            )
            ai_generations.insert_one(gen_model.to_dict())
        except Exception as log_err:
            print(f"[Orchestrator] Error logging provider error: {log_err}")
            
        return {
            "success": False,
            "status": 502,
            "message": "AI Image Generation Provider error. Please try again later."
        }

    # 7. Upload to Cloudinary (under folder galxy/ai-previews/)
    try:
        upload_result = cloudinary.uploader.upload(
            image_bytes,
            folder="galxy/ai-previews/",
            allowed_formats=["png", "jpg", "jpeg", "webp"]
        )
        output_image_url = upload_result.get("secure_url")
        if not output_image_url:
            raise Exception("Cloudinary secure_url missing from upload response.")
    except Exception as e:
        error_msg = f"Cloudinary upload failed: {str(e)}"
        print(f"[Orchestrator] {error_msg}")
        # Log failure in DB using AIGeneration model
        try:
            gen_model = AIGeneration(
                user_id=user_id,
                session_id=session_id,
                category_id=category_id,
                product_id=product_id,
                selected_attributes=selected_attributes,
                prompt_used=prompt_compiled,
                output_image_url="",
                provider=AI_PROVIDER,
                status="failed",
                error_message=error_msg,
                generation_time_ms=generation_time_ms
            )
            ai_generations.insert_one(gen_model.to_dict())
        except Exception as log_err:
            print(f"[Orchestrator] Error logging Cloudinary error: {log_err}")
            
        return {
            "success": False,
            "status": 502,
            "message": "Failed to store generated image."
        }

    # 8. Store in Caching tier
    store_cache(category_id, selected_attributes, output_image_url)

    # 9. Log successful generation history in DB using AIGeneration model
    try:
        gen_model = AIGeneration(
            user_id=user_id,
            session_id=session_id,
            category_id=category_id,
            product_id=product_id,
            selected_attributes=selected_attributes,
            prompt_used=prompt_compiled,
            output_image_url=output_image_url,
            provider=AI_PROVIDER,
            status="success",
            error_message=None,
            generation_time_ms=generation_time_ms
        )
        log_result = ai_generations.insert_one(gen_model.to_dict())
        generation_id = str(log_result.inserted_id)
    except Exception as e:
        print(f"[Orchestrator] Error logging successful generation: {e}")
        generation_id = "success_unlogged"

    # 10. Return success response payload
    return {
        "success": True,
        "status": 200,
        "data": {
            "output_image_url": output_image_url,
            "from_cache": False,
            "generation_id": generation_id,
            "disclaimer": "AI-generated approximation — final product may vary."
        }
    }
