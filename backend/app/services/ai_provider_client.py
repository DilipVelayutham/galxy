<<<<<<< HEAD
import os
import time
import base64
import urllib.request
import google.generativeai as genai
from app.configs.ai_config import GEMINI_API_KEY, MOCK_AI, AI_GENERATION_TIMEOUT_SECONDS

# Local minimal transparent 1x1 PNG fallback bytes if everything fails
TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

def generate_preview_image(prompt):
    """
    Calls the Gemini Imagen API to generate an image based on the prompt.
    Falls back to a Mock/Simulation Mode if keys are missing or MOCK_AI=True.
    """
    if MOCK_AI or not GEMINI_API_KEY:
        print(f"[AI Client] Mock Mode Active. Simulating image generation for prompt: '{prompt}'")
        if not os.getenv("TESTING"):
            time.sleep(1.5)  # Simulate generation delay
        return get_mock_image_bytes(prompt)

    try:
        # Initialize Google GenAI
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Access the Image Generation model (Imagen 3)
        model = genai.ImageGenerationModel("imagen-3.0-generate-002")
        
        # Call API (timeout can be enforced in outer call or handled naturally)
        result = model.generate_images(
            prompt=prompt,
            number_of_images=1
        )
        
        if result and result.images:
            image_obj = result.images[0]
            return image_obj.image.bytes
        else:
            raise Exception("No image returned from Gemini Imagen API.")
            
    except Exception as e:
        print(f"[AI Client] Real Gemini API call failed: {e}. Falling back to Mock Image.")
        return get_mock_image_bytes(prompt)

def get_mock_image_bytes(prompt):
    """Generates mock image bytes by downloading a high-quality product mockup or using base64 fallback."""
    # Fast mock: return local placeholder bytes instantly in Mock AI mode to eliminate network dependency/latency
    if MOCK_AI:
        return base64.b64decode(TINY_PNG_B64)
    # List of high-quality custom product mockups from Unsplash based on keywords
    default_url = "https://images.unsplash.com/photo-1563245372-f21724e3856d?q=80&w=600&auto=format&fit=crop" # Neon sign mockup
    
    url = default_url
    prompt_lower = prompt.lower()
    
    if "mug" in prompt_lower or "drinkware" in prompt_lower:
        url = "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?q=80&w=600&auto=format&fit=crop" # Mug mockup
    elif "case" in prompt_lower or "phone" in prompt_lower:
        url = "https://images.unsplash.com/photo-1603302576837-37561b2e2302?q=80&w=600&auto=format&fit=crop" # Phone case mockup
    elif "apparel" in prompt_lower or "shirt" in prompt_lower or "garment" in prompt_lower:
        url = "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?q=80&w=600&auto=format&fit=crop" # T-shirt mockup
        
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"[AI Client] Failed to download mock image online: {e}. Using local PNG bytes.")
        return base64.b64decode(TINY_PNG_B64)
=======
"""
ai_provider_client.py — Module 5 AI Preview Generation (T2)
Thin adapter layer around AI provider SDKs.

Design: adapter/interface pattern — one function per provider.
The AI_PROVIDER env var selects which provider to call at runtime.
Adding a new provider = add one function + register it in PROVIDER_REGISTRY.
Never call provider SDKs directly from ai_service.py — always go through here.
"""
import io
import logging
import time
import base64
from typing import Callable

from app.configs.ai_config import (
    AI_PROVIDER,
    GEMINI_API_KEY,
    AI_GENERATION_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)


# ─── Public interface ─────────────────────────────────────────────────────────────

def generate_image(
    prompt: str,
    reference_image_url: str | None = None,
) -> bytes:
    """
    Call the configured AI provider and return the raw image bytes.

    Args:
        prompt: The fully assembled prompt from prompt_builder_service.
        reference_image_url: Optional Cloudinary URL of a reference image
                             (e.g. customer's uploaded sketch).

    Returns:
        Raw PNG/JPEG image bytes from the provider.

    Raises:
        ProviderTimeoutError: if the provider exceeds AI_GENERATION_TIMEOUT_SECONDS.
        ProviderError: for any other provider-level failure.
    """
    provider_fn: Callable = _get_provider_fn(AI_PROVIDER)
    return provider_fn(
        prompt=prompt,
        reference_image_url=reference_image_url,
        timeout_seconds=AI_GENERATION_TIMEOUT_SECONDS,
    )


# ─── Provider registry ────────────────────────────────────────────────────────────

def _get_provider_fn(provider: str) -> Callable:
    """Return the provider function from the registry. Raises if unknown."""
    registry = {
        "gemini": _call_gemini,
        # future providers: "openai": _call_openai, "stability": _call_stability
    }
    fn = registry.get(provider.lower())
    if fn is None:
        raise ValueError(
            f"Unknown AI_PROVIDER '{provider}'. "
            f"Valid options: {list(registry.keys())}"
        )
    return fn


# ─── Gemini provider ──────────────────────────────────────────────────────────────

def _call_gemini(
    prompt: str,
    reference_image_url: str | None,
    timeout_seconds: int,
) -> bytes:
    """
    Call Google Gemini (free-tier) to generate an image.
    Uses the google-generativeai SDK.

    Returns raw image bytes on success.
    Raises ProviderTimeoutError or ProviderError on failure.
    """
    try:
        import google.generativeai as genai
        from google.generativeai import types as genai_types
    except ImportError as e:
        raise ProviderError(
            "google-generativeai package not installed. "
            "Run: pip install google-generativeai"
        ) from e

    if not GEMINI_API_KEY:
        raise ProviderError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )

    genai.configure(api_key=GEMINI_API_KEY)

    # Use the Gemini image generation model.
    # Model: gemini-2.0-flash-exp supports image output
    model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")

    # Build the content parts.
    contents: list = [prompt]
    if reference_image_url:
        ref_bytes = _fetch_image_bytes(reference_image_url, timeout_seconds)
        if ref_bytes:
            contents.append(
                genai_types.Part.from_bytes(
                    data=ref_bytes,
                    mime_type="image/jpeg",
                )
            )

    logger.info("[Gemini] Sending prompt (%d chars) to Gemini API…", len(prompt))
    start = time.monotonic()

    try:
        response = model.generate_content(
            contents=contents,
            generation_config=genai_types.GenerationConfig(
                response_modalities=["IMAGE"],
            ),
            request_options={"timeout": timeout_seconds},
        )
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        # Check if it's a timeout-flavored error
        exc_str = str(exc).lower()
        if "timeout" in exc_str or "deadline" in exc_str:
            raise ProviderTimeoutError(
                f"Gemini API timed out after {elapsed}ms."
            ) from exc
        raise ProviderError(
            f"Gemini API call failed after {elapsed}ms."
        ) from exc

    elapsed_ms = int((time.monotonic() - start) * 1000)
    logger.info("[Gemini] Response received in %dms.", elapsed_ms)

    # Extract image bytes from the response
    image_bytes = _extract_gemini_image_bytes(response)
    return image_bytes


def _extract_gemini_image_bytes(response) -> bytes:
    """
    Navigate the Gemini response object to find and return raw image bytes.
    Raises ProviderError if no image data is found.
    """
    try:
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    return part.inline_data.data
                # Some SDK versions return blob data differently
                if hasattr(part, "blob") and part.blob:
                    return part.blob.data
    except Exception as exc:
        raise ProviderError(
            "Could not parse image data from Gemini response."
        ) from exc

    raise ProviderError(
        "Gemini response contained no image data. "
        "The model may have declined the request or returned only text."
    )


def _fetch_image_bytes(url: str, timeout_seconds: int) -> bytes | None:
    """Download image bytes from a URL. Returns None on failure (non-fatal)."""
    try:
        import requests
        resp = requests.get(url, timeout=timeout_seconds)
        resp.raise_for_status()
        return resp.content
    except Exception as exc:
        logger.warning(
            "Could not fetch reference image from '%s': %s. "
            "Continuing without reference image.",
            url,
            exc,
        )
        return None


# ─── Custom exceptions ────────────────────────────────────────────────────────────

class ProviderTimeoutError(Exception):
    """Raised when the AI provider exceeds the configured timeout."""


class ProviderError(Exception):
    """Raised for any non-timeout provider-level failure."""
>>>>>>> origin/main
