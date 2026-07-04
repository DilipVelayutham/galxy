"""
ai_service.py — Module 5 AI Preview Generation
Core orchestration engine for AI preview generation.
"""
import os
import time
import datetime
import logging
from bson import ObjectId
import cloudinary.uploader
import cloudinary

from app.database import categories, ai_generations
from app.configs.ai_config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
    CLOUDINARY_AI_PREVIEW_FOLDER,
    AI_PROVIDER,
)
from app.models.ai_generation import AIGeneration
from app.services import ai_cache_service
from app.services import ai_rate_limit_service
from app.services import prompt_builder_service
from app.services import ai_provider_client
from app.services.ai_provider_client import ProviderTimeoutError, ProviderError
from app.utils.db_helpers import get_category_by_id
from app.utils.module4_client import validate_attributes as m4_validate

logger = logging.getLogger(__name__)

# Cache initialization state
_cloudinary_initialized = False


def init_cloudinary():
    """Configure the Cloudinary SDK if not already done."""
    global _cloudinary_initialized
    if not _cloudinary_initialized:
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True,
        )
        _cloudinary_initialized = True


_last_uploaded_public_id = None


def upload_preview_image(image_bytes: bytes, category_id: str) -> str:
    """Uploads preview image and stores the public_id for orphan handling/rollback."""
    global _last_uploaded_public_id
    init_cloudinary()
    import io
    import time
    public_id = f"{CLOUDINARY_AI_PREVIEW_FOLDER}/gen_{category_id}_{int(time.time())}"
    res = cloudinary.uploader.upload(
        io.BytesIO(image_bytes),
        public_id=public_id,
        resource_type="image",
        overwrite=False,
        unique_filename=True,
    )
    url = res.get("secure_url", "")
    _last_uploaded_public_id = res.get("public_id", public_id)
    return url


def _extract_public_id(url: str) -> str | None:
    if not url or "cloudinary.com" not in url:
        return None
    try:
        parts = url.split("/upload/")
        if len(parts) > 1:
            subparts = parts[1].split("/")
            start_idx = 1 if subparts[0].startswith("v") else 0
            path_parts = subparts[start_idx:]
            full_path = "/".join(path_parts)
            if "." in full_path:
                full_path = full_path.rsplit(".", 1)[0]
            return full_path
    except Exception:
        pass
    return None


# ─── Structured Output Class with Dict Compatibility ─────────────────────────────────

class GenerationResult:
    """
    Result of an AI preview generation.
    Supports attribute access (for new code) and dictionary access (for legacy code).
    """
    def __init__(
        self,
        success: bool,
        output_image_url: str | None = None,
        from_cache: bool = False,
        generation_id: str | None = None,
        disclaimer: str = "AI-generated approximation — final product may vary.",
        error_code: int | None = None,
        error_message: str | None = None,
        limit_reached: bool = False,
        limit_scope: str = "",
        errors: list = None,
    ):
        self.success = success
        self.output_image_url = output_image_url
        self.from_cache = from_cache
        self.generation_id = generation_id
        self.disclaimer = disclaimer
        self.error_code = error_code
        self.error_message = error_message
        self.limit_reached = limit_reached
        self.limit_scope = limit_scope
        self.errors = errors or []

    def __getitem__(self, key):
        if key == "success":
            return self.success
        if key == "status":
            return self.error_code or (200 if self.success else 500)
        if key == "message":
            return self.error_message
        if key == "errors":
            return self.errors
        if key == "data":
            return {
                "output_image_url": self.output_image_url,
                "from_cache": self.from_cache,
                "generation_id": self.generation_id,
                "disclaimer": self.disclaimer,
            }
        if key == "limit_reached":
            return self.limit_reached
        if key == "limit_scope":
            return self.limit_scope
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


# ─── Core Orchestrator ──────────────────────────────────────────────────────────────

def generate_preview(
    category_id: str,
    selected_attributes: dict,
    user_id: str | None = None,
    session_id: str | None = None,
    ip_address: str | None = None,
    product_id: str | None = None,
    input_reference_image: str | None = None,
) -> GenerationResult:
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
    category = get_category_by_id(category_id)
    if not category:
        return GenerationResult(
            success=False,
            error_code=400,
            error_message=f"Category '{category_id}' not found.",
        )

    # Normalize category dictionary representation to support both validation branches
    if "attributes" not in category and "attribute_schema" in category:
        category["attributes"] = category["attribute_schema"]
    elif "attribute_schema" not in category and "attributes" in category:
        category["attribute_schema"] = category["attributes"]

    # 2. Call Module 4's validation engine
    val_res = m4_validate(category, selected_attributes)
    if not val_res.get("valid"):
        return GenerationResult(
            success=False,
            error_code=400,
            error_message="Invalid attributes selected.",
            errors=val_res.get("errors", []),
        )

    # 3. Check Caching tier
    use_cache = not ai_cache_service.has_custom_text(selected_attributes, category)
    if use_cache:
        cached_url = ai_cache_service.check_cache(category_id, selected_attributes)
        if cached_url:
            # Build prompt compiled purely for logging history
            prompt_compiled = ""
            try:
                prompt_compiled = prompt_builder_service.build_prompt(category, selected_attributes)
            except Exception:
                pass

            # Log cache hit in DB using AIGeneration model (generation_time_ms = 0)
            try:
                doc = {
                    "user_id": ObjectId(user_id) if user_id and len(str(user_id)) == 24 else user_id,
                    "session_id": session_id,
                    "ip_address": ip_address,
                    "category_id": ObjectId(category_id) if category_id and len(str(category_id)) == 24 else category_id,
                    "product_id": ObjectId(product_id) if product_id and len(str(product_id)) == 24 else product_id,
                    "selected_attributes": selected_attributes,
                    "prompt_used": prompt_compiled or "(served from cache)",
                    "input_reference_image": input_reference_image,
                    "output_image_url": cached_url,
                    "provider": AI_PROVIDER,
                    "status": "success",
                    "error_message": None,
                    "generation_time_ms": 0,
                    "created_at": datetime.datetime.now(datetime.timezone.utc),
                }
                res = ai_generations.insert_one(doc)
                generation_id = str(res.inserted_id)
            except Exception as e:
                logger.error("[Orchestrator] Error logging cache hit: %s", e)
                generation_id = "cache_hit_unlogged"

            return GenerationResult(
                success=True,
                output_image_url=cached_url,
                from_cache=True,
                generation_id=generation_id,
            )

    # 4. Check Rate Limiting tier
    rate_result = ai_rate_limit_service.check_rate_limit(
        session_id=session_id,
        user_id=user_id,
        ip_address=ip_address,
    )
    if not rate_result.allowed:
        # Log rate limited state in DB
        try:
            doc = {
                "user_id": ObjectId(user_id) if user_id and len(str(user_id)) == 24 else user_id,
                "session_id": session_id,
                "ip_address": ip_address,
                "category_id": ObjectId(category_id) if category_id and len(str(category_id)) == 24 else category_id,
                "product_id": ObjectId(product_id) if product_id and len(str(product_id)) == 24 else product_id,
                "selected_attributes": selected_attributes,
                "prompt_used": "",
                "input_reference_image": input_reference_image,
                "output_image_url": "",
                "provider": AI_PROVIDER,
                "status": "rate_limited",
                "error_message": f"Rate limit reached for {rate_result.limit_scope}",
                "generation_time_ms": 0,
                "created_at": datetime.datetime.now(datetime.timezone.utc),
            }
            ai_generations.insert_one(doc)
        except Exception as e:
            logger.error("[Orchestrator] Error logging rate limit block: %s", e)
            
        scope = "session" if rate_result.limit_scope == "guest" else (rate_result.limit_scope or "session")
        return GenerationResult(
            success=False,
            error_code=429,
            error_message="AI generation rate limit reached.",
            limit_reached=True,
            limit_scope=scope,
        )

    # 5. Build prompt
    try:
        prompt_compiled = prompt_builder_service.build_prompt(category, selected_attributes)
    except ValueError as exc:
        return GenerationResult(
            success=False,
            error_code=400,
            error_message=str(exc),
        )

    # 6. Call provider to generate image
    start_time = time.time()
    try:
        image_bytes = ai_provider_client.generate_image(
            prompt=prompt_compiled,
            reference_image_url=input_reference_image,
        )
        generation_time_ms = max(int((time.time() - start_time) * 1000), 1)
    except ProviderTimeoutError as exc:
        error_msg = "AI provider request timed out. Please try again later."
        try:
            doc = {
                "user_id": ObjectId(user_id) if user_id and len(str(user_id)) == 24 else user_id,
                "session_id": session_id,
                "ip_address": ip_address,
                "category_id": ObjectId(category_id) if category_id and len(str(category_id)) == 24 else category_id,
                "product_id": ObjectId(product_id) if product_id and len(str(product_id)) == 24 else product_id,
                "selected_attributes": selected_attributes,
                "prompt_used": prompt_compiled,
                "input_reference_image": input_reference_image,
                "output_image_url": "",
                "provider": AI_PROVIDER,
                "status": "failed",
                "error_message": error_msg,
                "generation_time_ms": int((time.time() - start_time) * 1000),
                "created_at": datetime.datetime.now(datetime.timezone.utc),
            }
            ai_generations.insert_one(doc)
        except Exception as log_err:
            logger.error("[Orchestrator] Error logging timeout failure: %s", log_err)
        return GenerationResult(
            success=False,
            error_code=504,
            error_message=error_msg,
        )
    except Exception as e:
        error_msg = str(e)
        try:
            doc = {
                "user_id": ObjectId(user_id) if user_id and len(str(user_id)) == 24 else user_id,
                "session_id": session_id,
                "ip_address": ip_address,
                "category_id": ObjectId(category_id) if category_id and len(str(category_id)) == 24 else category_id,
                "product_id": ObjectId(product_id) if product_id and len(str(product_id)) == 24 else product_id,
                "selected_attributes": selected_attributes,
                "prompt_used": prompt_compiled,
                "input_reference_image": input_reference_image,
                "output_image_url": "",
                "provider": AI_PROVIDER,
                "status": "failed",
                "error_message": error_msg,
                "generation_time_ms": int((time.time() - start_time) * 1000),
                "created_at": datetime.datetime.now(datetime.timezone.utc),
            }
            ai_generations.insert_one(doc)
        except Exception as log_err:
            logger.error("[Orchestrator] Error logging provider failure: %s", log_err)
            
        return GenerationResult(
            success=False,
            error_code=502,
            error_message="AI Image Generation Provider error. Please try again later.",
        )

    # 7. Upload to Cloudinary (under folder galxy/ai-previews/)
    try:
        output_image_url = upload_preview_image(image_bytes, category_id)
        public_id = _last_uploaded_public_id or _extract_public_id(output_image_url)
    except Exception as e:
        error_msg = f"Cloudinary upload failed: {str(e)}"
        logger.error("[Orchestrator] %s", error_msg)
        try:
            doc = {
                "user_id": ObjectId(user_id) if user_id and len(str(user_id)) == 24 else user_id,
                "session_id": session_id,
                "ip_address": ip_address,
                "category_id": ObjectId(category_id) if category_id and len(str(category_id)) == 24 else category_id,
                "product_id": ObjectId(product_id) if product_id and len(str(product_id)) == 24 else product_id,
                "selected_attributes": selected_attributes,
                "prompt_used": prompt_compiled,
                "input_reference_image": input_reference_image,
                "output_image_url": "",
                "provider": AI_PROVIDER,
                "status": "failed",
                "error_message": error_msg,
                "generation_time_ms": generation_time_ms,
                "created_at": datetime.datetime.now(datetime.timezone.utc),
            }
            ai_generations.insert_one(doc)
        except Exception as log_err:
            logger.error("[Orchestrator] Error logging Cloudinary error: %s", log_err)
            
        return GenerationResult(
            success=False,
            error_code=502,
            error_message="Failed to store generated image.",
        )

    # 8. Store in Caching tier and 9. Log successful generation history in DB
    try:
        ai_cache_service.store_cache(category_id, selected_attributes, output_image_url)

        doc = {
            "user_id": ObjectId(user_id) if user_id and len(str(user_id)) == 24 else user_id,
            "session_id": session_id,
            "ip_address": ip_address,
            "category_id": ObjectId(category_id) if category_id and len(str(category_id)) == 24 else category_id,
            "product_id": ObjectId(product_id) if product_id and len(str(product_id)) == 24 else product_id,
            "selected_attributes": selected_attributes,
            "prompt_used": prompt_compiled,
            "input_reference_image": input_reference_image,
            "output_image_url": output_image_url,
            "provider": AI_PROVIDER,
            "status": "success",
            "error_message": None,
            "generation_time_ms": generation_time_ms,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        }
        res = ai_generations.insert_one(doc)
        generation_id = str(res.inserted_id)
    except Exception as e:
        logger.error("[Orchestrator] Error saving database record or cache: %s", e)
        # Perform Cloudinary Rollback (Orphan Handling)
        if public_id:
            try:
                init_cloudinary()
                cloudinary.uploader.destroy(public_id)
                logger.info("[Orchestrator] Rolled back Cloudinary image (destroyed orphan): %s", public_id)
            except Exception as destroy_err:
                logger.error("[Orchestrator] Failed to destroy orphaned Cloudinary image %s: %s", public_id, destroy_err)
        
        # Log failure in DB
        error_msg = f"Database save failed after Cloudinary upload: {str(e)}"
        try:
            doc = {
                "user_id": ObjectId(user_id) if user_id and len(str(user_id)) == 24 else user_id,
                "session_id": session_id,
                "ip_address": ip_address,
                "category_id": ObjectId(category_id) if category_id and len(str(category_id)) == 24 else category_id,
                "product_id": ObjectId(product_id) if product_id and len(str(product_id)) == 24 else product_id,
                "selected_attributes": selected_attributes,
                "prompt_used": prompt_compiled,
                "input_reference_image": input_reference_image,
                "output_image_url": "",
                "provider": AI_PROVIDER,
                "status": "failed",
                "error_message": error_msg,
                "generation_time_ms": generation_time_ms,
                "created_at": datetime.datetime.now(datetime.timezone.utc),
            }
            ai_generations.insert_one(doc)
        except Exception as log_err:
            logger.error("[Orchestrator] Error logging database save error: %s", log_err)
            
        return GenerationResult(
            success=False,
            error_code=502,
            error_message="Failed to store generated image.",
        )

    # 10. Return success response payload
    return GenerationResult(
        success=True,
        output_image_url=output_image_url,
        from_cache=False,
        generation_id=generation_id,
    )
