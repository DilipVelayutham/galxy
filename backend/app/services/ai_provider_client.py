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
