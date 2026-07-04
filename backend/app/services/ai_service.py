<<<<<<< HEAD
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

def generate_preview(category_id, selected_attributes, user_id=None, session_id=None, ip_address=None, product_id=None):
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
    cache_result = check_cache(category, selected_attributes)
    if cache_result.get("hit"):
        cached_url = cache_result.get("output_image_url")
        prompt_compiled = build_prompt(category, selected_attributes)
        
        # Log cache hit in DB using AIGeneration model (generation_time_ms = 0)
        try:
            gen_model = AIGeneration(
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
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
    rate_result = check_rate_limit(user_id=user_id, session_id=session_id, ip_address=ip_address)
    if not rate_result.get("allowed"):
        # Log rate limited state in DB using AIGeneration model
        try:
            gen_model = AIGeneration(
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
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
        generation_time_ms = max(int((time.time() - start_time) * 1000), 1)
    except Exception as e:
        error_msg = str(e)
        # Log failure in DB using AIGeneration model
        try:
            gen_model = AIGeneration(
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
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
    public_id = None
    try:
        upload_result = cloudinary.uploader.upload(
            image_bytes,
            folder="galxy/ai-previews/",
            allowed_formats=["png", "jpg", "jpeg", "webp"]
        )
        output_image_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")
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
                ip_address=ip_address,
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

    # 8. Store in Caching tier and 9. Log successful generation history in DB
    try:
        store_cache(category, selected_attributes, output_image_url)

        gen_model = AIGeneration(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
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
        print(f"[Orchestrator] Error saving database record or cache: {e}")
        # Perform Cloudinary Rollback (Orphan Handling)
        if public_id:
            try:
                cloudinary.uploader.destroy(public_id)
                print(f"[Orchestrator] Rolled back Cloudinary image (destroyed orphan): {public_id}")
            except Exception as destroy_err:
                print(f"[Orchestrator] Failed to destroy orphaned Cloudinary image {public_id}: {destroy_err}")
        
        # Log failure in DB
        error_msg = f"Database save failed after Cloudinary upload: {str(e)}"
        try:
            gen_model = AIGeneration(
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
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
            print(f"[Orchestrator] Error logging database save error: {log_err}")
            
        return {
            "success": False,
            "status": 502,
            "message": "Failed to store generated image."
        }

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
=======
"""
ai_service.py — Module 5 AI Preview Generation
Core orchestration engine for AI preview generation.

Pipeline (per spec §6 & Intern Review):
  1. Receive: category_id, product_id?, selected_attributes, session_id/user_id
  2. Validate attributes via Module 4 (delegate — never re-implement)
     └─ 400 if invalid (never waste a paid generation)
  3. Check cache (ai_cache_service)
     └─ If cache hit, return cached URL immediately (non-cached, free).
  4. Check rate limit (ai_rate_limit_service)
     └─ If over quota, block with 429. Only genuine provider calls consume quota.
  5. Build prompt (prompt_builder_service)
  6. Call AI provider (ai_provider_client) with timeout
  7a. Success → upload to Cloudinary → log ai_generations ➔ return URL
  7b. Failure → log ai_generations with failed status ➔ return clean error
"""
import logging
import time
from bson import ObjectId

from app.configs.ai_config import AI_PROVIDER
from app.models import ai_generation as ai_gen_model
from app.services import prompt_builder_service
from app.services import ai_provider_client
from app.services.ai_provider_client import ProviderTimeoutError, ProviderError
from app.services import ai_cache_service
from app.services import ai_rate_limit_service
from app.utils.module4_client import validate_attributes as m4_validate
from app.utils.db_helpers import get_category_by_id
from app.utils.cloudinary_helper import upload_preview_image

logger = logging.getLogger(__name__)


# ─── Structured Output Class ──────────────────────────────────────────────────────

class GenerationResult:
    """Structured result returned by generate_preview()."""
    def __init__(
        self,
        *,
        success: bool,
        output_image_url: str = "",
        generation_id: str = "",
        from_cache: bool = False,
        disclaimer: str = "AI-generated approximation — final product may vary.",
        error_code: int = 0,
        error_message: str = "",
        limit_reached: bool = False,
        limit_scope: str = "",
    ):
        self.success = success
        self.output_image_url = output_image_url
        self.generation_id = generation_id
        self.from_cache = from_cache
        self.disclaimer = disclaimer
        self.error_code = error_code
        self.error_message = error_message
        self.limit_reached = limit_reached
        self.limit_scope = limit_scope


# ─── Orchestration Pipeline ──────────────────────────────────────────────────────

def generate_preview(
    *,
    category_id: str,
    product_id: str | None,
    selected_attributes: dict,
    session_id: str,
    user_id: str | None,
    input_reference_image: str | None = None,
) -> GenerationResult:
    """
    Orchestrate the full AI preview generation pipeline.

    Args:
        category_id: string ObjectId of the product category.
        product_id: string ObjectId (or None for fully custom).
        selected_attributes: raw dict from the request body.
        session_id: guest UUID or logged-in user's session UUID.
        user_id: string ObjectId if logged in, None if guest.
        input_reference_image: optional Cloudinary URL for reference image.
    """
    # ── Step 1: Fetch category from DB ────────────────────────────────────────────
    category = get_category_by_id(category_id)
    if category is None:
        return GenerationResult(
            success=False,
            error_code=400,
            error_message=f"Category '{category_id}' not found.",
        )

    # ── Step 2: Validate attributes via Module 4 ──────────────────────────────────
    validation_result = m4_validate(
        category=category,
        selected_attributes=selected_attributes,
    )
    if not validation_result["valid"]:
        logger.info(
            "[ai_service] Attribute validation failed for category=%s: %s",
            category_id,
            validation_result.get("errors"),
        )
        return GenerationResult(
            success=False,
            error_code=400,
            error_message=validation_result.get("message", "Invalid attributes."),
        )

    # ── Step 3: Rate limit check ──────────────────────────────────────────────────
    rate_result = ai_rate_limit_service.check_rate_limit(
        session_id=session_id,
        user_id=user_id,
    )
    if not rate_result.allowed:
        logger.info(
            "[ai_service] Rate limit exceeded: scope=%s session=%s user=%s",
            rate_result.limit_scope,
            session_id,
            user_id,
        )
        # Log rate-limited generation.
        try:
            doc = ai_gen_model.build_document(
                user_id=ObjectId(user_id) if user_id else None,
                session_id=session_id,
                category_id=ObjectId(category_id),
                product_id=ObjectId(product_id) if product_id else None,
                selected_attributes=selected_attributes,
                prompt_used="(rate limited)",
                input_reference_image=input_reference_image,
                output_image_url="",
                provider=AI_PROVIDER,
                status="rate_limited",
                error_message=rate_result.message,
                generation_time_ms=0,
            )
            ai_gen_model.insert_generation(doc)
        except Exception as exc:
            logger.error("[ai_service] Failed to log rate-limited generation: %s", exc)

        return GenerationResult(
            success=False,
            error_code=429,
            error_message=rate_result.message,
            limit_reached=True,
            limit_scope=rate_result.limit_scope,
        )

    # ── Step 4: Cache check ───────────────────────────────────────────────────────
    # If a cache entry is hit, serve it directly without decrementing user quotas.
    use_cache = not ai_cache_service.has_custom_text(selected_attributes, category)

    if use_cache:
        cached_url = ai_cache_service.check_cache(category_id, selected_attributes)
        if cached_url:
            logger.info(
                "[ai_service] Cache HIT for category=%s — returning cached URL directly.",
                category_id,
            )
            # Log successful generation (0ms, cache flag).
            doc = ai_gen_model.build_document(
                user_id=ObjectId(user_id) if user_id else None,
                session_id=session_id,
                category_id=ObjectId(category_id),
                product_id=ObjectId(product_id) if product_id else None,
                selected_attributes=selected_attributes,
                prompt_used="(served from cache)",
                input_reference_image=input_reference_image,
                output_image_url=cached_url,
                provider=AI_PROVIDER,
                status="success",
                generation_time_ms=0,
            )
            gen_id = ai_gen_model.insert_generation(doc)
            return GenerationResult(
                success=True,
                output_image_url=cached_url,
                generation_id=gen_id,
                from_cache=True,
            )

    # ── Step 5: Build prompt ──────────────────────────────────────────────────────
    try:
        prompt_used = prompt_builder_service.build_prompt(
            category=category,
            selected_attributes=selected_attributes,
        )
    except ValueError as exc:
        logger.error("[ai_service] Prompt build failed: %s", exc)
        return GenerationResult(
            success=False,
            error_code=400,
            error_message=str(exc),
        )

    # ── Step 6: Call AI provider ──────────────────────────────────────────────────
    start_ms = int(time.monotonic() * 1000)
    image_bytes: bytes | None = None
    provider_error: str | None = None
    error_code = 0

    try:
        image_bytes = ai_provider_client.generate_image(
            prompt=prompt_used,
            reference_image_url=input_reference_image,
        )
    except ProviderTimeoutError as exc:
        logger.warning("[ai_service] Provider timeout: %s", exc)
        provider_error = "The AI provider timed out. Please try again."
        error_code = 504
    except ProviderError as exc:
        logger.error("[ai_service] Provider error: %s", exc)
        provider_error = "The AI provider encountered an error. Please try again."
        error_code = 502
    except Exception as exc:
        logger.exception("[ai_service] Unexpected error during generation: %s", exc)
        provider_error = "An unexpected error occurred. Please try again."
        error_code = 502

    generation_time_ms = int(time.monotonic() * 1000) - start_ms

    # ── Step 7b: Failure path ─────────────────────────────────────────────────────
    if provider_error or image_bytes is None:
        status = "failed"
        doc = ai_gen_model.build_document(
            user_id=ObjectId(user_id) if user_id else None,
            session_id=session_id,
            category_id=ObjectId(category_id),
            product_id=ObjectId(product_id) if product_id else None,
            selected_attributes=selected_attributes,
            prompt_used=prompt_used,
            input_reference_image=input_reference_image,
            output_image_url="",
            provider=AI_PROVIDER,
            status=status,
            error_message=provider_error,
            generation_time_ms=generation_time_ms,
        )
        ai_gen_model.insert_generation(doc)
        return GenerationResult(
            success=False,
            error_code=error_code or 502,
            error_message=provider_error or "Unknown provider error.",
        )

    # ── Step 7a: Success path — upload to Cloudinary ──────────────────────────────
    try:
        output_image_url = upload_preview_image(
            image_bytes=image_bytes,
            category_id=category_id,
        )
    except Exception as exc:
        logger.error("[ai_service] Cloudinary upload failed: %s", exc)
        doc = ai_gen_model.build_document(
            user_id=ObjectId(user_id) if user_id else None,
            session_id=session_id,
            category_id=ObjectId(category_id),
            product_id=ObjectId(product_id) if product_id else None,
            selected_attributes=selected_attributes,
            prompt_used=prompt_used,
            input_reference_image=input_reference_image,
            output_image_url="",
            provider=AI_PROVIDER,
            status="failed",
            error_message="Image upload failed after generation.",
            generation_time_ms=generation_time_ms,
        )
        ai_gen_model.insert_generation(doc)
        return GenerationResult(
            success=False,
            error_code=502,
            error_message="Generated image could not be saved. Please try again.",
        )

    # Log successful generation.
    doc = ai_gen_model.build_document(
        user_id=ObjectId(user_id) if user_id else None,
        session_id=session_id,
        category_id=ObjectId(category_id),
        product_id=ObjectId(product_id) if product_id else None,
        selected_attributes=selected_attributes,
        prompt_used=prompt_used,
        input_reference_image=input_reference_image,
        output_image_url=output_image_url,
        provider=AI_PROVIDER,
        status="success",
        generation_time_ms=generation_time_ms,
    )
    gen_id = ai_gen_model.insert_generation(doc)

    # Cache successful result.
    if use_cache:
        ai_cache_service.store_cache(category_id, selected_attributes, output_image_url)

    logger.info(
        "[ai_service] Generation SUCCESS: gen_id=%s category=%s time=%dms",
        gen_id,
        category_id,
        generation_time_ms,
    )

    return GenerationResult(
        success=True,
        output_image_url=output_image_url,
        generation_id=gen_id,
        from_cache=False,
    )
>>>>>>> origin/main
