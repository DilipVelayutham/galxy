"""
ai_service.py — Module 5 AI Preview Generation (T1 — Backend Member 1)
Core orchestration engine for AI preview generation.

Pipeline (per spec §6):
  1. Receive: category_id, product_id?, selected_attributes, session_id/user_id
  2. Validate attributes via Module 4 (delegate — never re-implement)
  3. Check rate limit (ai_rate_limit_service)        ← no AI call if exceeded
  4. Check cache (ai_cache_service)                  ← return instantly if hit
  5. Build prompt (prompt_builder_service)
  6. Call AI provider (ai_provider_client) with timeout
  7a. Success → upload to Cloudinary → log ai_generations → return URL
  7b. Failure → log ai_generations with failed status → return clean error

OWNER: Naveen Kumar D (Backend Member 1, feat-m5-t1-core-prompt)
"""
import io
import logging
import time
from bson import ObjectId

import cloudinary
import cloudinary.uploader

from app.configs.ai_config import (
    AI_PROVIDER,
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
    CLOUDINARY_AI_PREVIEW_FOLDER,
)
from app.models import ai_generation as ai_gen_model
from app.services import prompt_builder_service
from app.services import ai_provider_client
from app.services.ai_provider_client import ProviderTimeoutError, ProviderError
from app.services import ai_cache_service
from app.services import ai_rate_limit_service
from app.utils.module4_client import validate_attributes as m4_validate
from app.utils.db_helpers import get_category_by_id

logger = logging.getLogger(__name__)

# ─── Cloudinary initializer ───────────────────────────────────────────────────────
def _init_cloudinary():
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )


# ─── Main entry point ─────────────────────────────────────────────────────────────

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
        session_id: guest UUID or logged-in user's session UUID (always present).
        user_id: string ObjectId if logged in, None if guest.
        input_reference_image: optional Cloudinary URL for reference image.

    Returns:
        GenerationResult with all fields the route handler needs to build
        the API response.
    """
    _init_cloudinary()

    # ── Step 1: Fetch category from DB ────────────────────────────────────────────
    category = get_category_by_id(category_id)
    if category is None:
        return GenerationResult(
            success=False,
            error_code=400,
            error_message=f"Category '{category_id}' not found.",
        )

    # ── Step 2: Validate attributes via Module 4 ──────────────────────────────────
    # Per spec: never waste a generation on a broken selection.
    # Never re-implement validation — always delegate.
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
    # Called BEFORE cache check so that genuine-new-call quota is only decremented
    # when a real provider call actually happens (cache hits are free; see Step 4).
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
        return GenerationResult(
            success=False,
            error_code=429,
            error_message=rate_result.message,
            limit_reached=True,
            limit_scope=rate_result.limit_scope,
        )

    # ── Step 4: Cache check ───────────────────────────────────────────────────────
    # Bypass cache if any selected attribute is a free-text/custom_text field.
    use_cache = not ai_cache_service.has_custom_text(selected_attributes, category)

    if use_cache:
        cached_url = ai_cache_service.check_cache(category_id, selected_attributes)
        if cached_url:
            logger.info(
                "[ai_service] Cache HIT for category=%s — returning cached URL.",
                category_id,
            )
            # Log a new generation record for analytics (generation_time_ms=0).
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
            # Note: cached hits do NOT increment rate-limit counters (spec §8).
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
        output_image_url = _upload_to_cloudinary(
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

    # Log the successful generation.
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

    # Store in cache (only if not a custom-text generation).
    if use_cache:
        ai_cache_service.store_cache(category_id, selected_attributes, output_image_url)

    # Increment rate-limit counter — only genuine new calls count (spec §8).
    ai_rate_limit_service.increment_usage(session_id=session_id, user_id=user_id)

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


# ─── Cloudinary upload helper ─────────────────────────────────────────────────────

def _upload_to_cloudinary(image_bytes: bytes, category_id: str) -> str:
    """
    Upload raw image bytes to the shared Cloudinary account under the
    galxy/ai-previews/ folder (spec §10).

    Returns the secure URL of the uploaded asset.
    Raises on any Cloudinary SDK error.
    """
    public_id = f"{CLOUDINARY_AI_PREVIEW_FOLDER}/gen_{category_id}_{int(time.time())}"
    result = cloudinary.uploader.upload(
        io.BytesIO(image_bytes),
        public_id=public_id,
        resource_type="image",
        overwrite=False,
        unique_filename=True,
    )
    url: str = result.get("secure_url", "")
    if not url:
        raise RuntimeError(
            "Cloudinary upload returned no secure_url. Response: " + str(result)
        )
    return url
