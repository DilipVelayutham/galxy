"""
ai_provider_client.py — Module 5 AI Preview Generation (T2)
Thin adapter layer around AI provider SDKs.
"""
import io
import logging
import time
import base64
import urllib.request
from typing import Callable

from app.configs.ai_config import (
    AI_PROVIDER,
    GEMINI_API_KEY,
    MOCK_AI,
    AI_GENERATION_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)

# Local minimal transparent 1x1 PNG fallback bytes if everything fails
TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="


# ─── Public interface ─────────────────────────────────────────────────────────────

def generate_image(
    prompt: str,
    reference_image_url: str | None = None,
) -> bytes:
    """
    Call the configured AI provider and return the raw image bytes.
    Falls back to mock image bytes if MOCK_AI is enabled or if GEMINI_API_KEY is missing.
    """
    if MOCK_AI or not GEMINI_API_KEY:
        logger.info("[AI Client] Mock Mode Active. Simulating image generation.")
        # Simulate delay when not in unit testing
        import os
        if not os.getenv("TESTING"):
            time.sleep(1.0)
        return get_mock_image_bytes(prompt)

    provider_fn: Callable = _get_provider_fn(AI_PROVIDER)
    return provider_fn(
        prompt=prompt,
        reference_image_url=reference_image_url,
        timeout_seconds=AI_GENERATION_TIMEOUT_SECONDS,
    )


def generate_preview_image(prompt: str) -> bytes:
    """Wrapper function for legacy callers (HEAD)."""
    return generate_image(prompt)


# ─── Mock Fallbacks ───────────────────────────────────────────────────────────────

def get_mock_image_bytes(prompt: str) -> bytes:
    """Generates mock image bytes by downloading a high-quality mockup or using base64 fallback."""
    prompt_lower = prompt.lower()
    default_url = "https://images.unsplash.com/photo-1563245372-f21724e3856d?q=80&w=600&auto=format&fit=crop" # Neon sign mockup
    
    url = default_url
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
        # Use a short timeout of 3 seconds to avoid blocking tests
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.read()
    except Exception as e:
        logger.warning("[AI Client] Failed to download mock image online: %s. Using local PNG bytes.", e)
        return base64.b64decode(TINY_PNG_B64)


# ─── Provider registry ────────────────────────────────────────────────────────────

def _get_provider_fn(provider: str) -> Callable:
    """Return the provider function from the registry. Raises if unknown."""
    registry = {
        "gemini": _call_gemini,
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
    Call Google Gemini to generate an image.
    Raises ProviderTimeoutError or ProviderError on failure.
    """
    try:
        import google.generativeai as genai
        from google.generativeai import types as genai_types
    except ImportError as e:
        raise ProviderError(
            "google-generativeai package not installed."
        ) from e

    if not GEMINI_API_KEY:
        raise ProviderError(
            "GEMINI_API_KEY is not set."
        )

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")

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

    image_bytes = _extract_gemini_image_bytes(response)
    return image_bytes


def _extract_gemini_image_bytes(response) -> bytes:
    """Navigate the Gemini response object to find and return raw image bytes."""
    try:
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    return part.inline_data.data
                if hasattr(part, "blob") and part.blob:
                    return part.blob.data
    except Exception as exc:
        raise ProviderError(
            "Could not parse image data from Gemini response."
        ) from exc

    raise ProviderError(
        "Gemini response contained no image data."
    )


def _fetch_image_bytes(url: str, timeout_seconds: int) -> bytes | None:
    """Download image bytes from a URL. Returns None on failure."""
    try:
        import requests
        resp = requests.get(url, timeout=timeout_seconds)
        resp.raise_for_status()
        return resp.content
    except Exception as exc:
        logger.warning(
            "Could not fetch reference image from '%s': %s.",
            url,
            exc,
        )
        return None


# ─── Custom exceptions ────────────────────────────────────────────────────────────

class ProviderTimeoutError(Exception):
    """Raised when the AI provider exceeds the configured timeout."""


class ProviderError(Exception):
    """Raised for any non-timeout provider-level failure."""

