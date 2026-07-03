import base64
import os
import requests
import struct

def generate_mock_image_bytes():
    # Create a simple 200x200 solid blue BMP image (no third-party dependencies required)
    width, height = 200, 200
    row_size = (width * 3 + 3) & ~3
    pixel_data_size = row_size * height
    file_size = 54 + pixel_data_size
    
    header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54)
    dib = struct.pack('<IiiHHIIiiII', 40, width, height, 1, 24, 0, pixel_data_size, 2835, 2835, 0, 0)
    
    pixels = bytearray()
    for y in range(height):
        row = bytearray()
        for x in range(width):
            row.extend([235, 128, 50])  # B, G, R (Cyan-ish blue)
        while len(row) % 4 != 0:
            row.append(0)
        pixels.extend(row)
        
    return header + dib + bytes(pixels)

def generate_image(prompt, input_reference_image=None):
    provider = os.getenv("AI_PROVIDER", "gemini")
    api_key = os.getenv("GEMINI_API_KEY")
    
    # If API key is missing or we are in mock mode, use local fallback
    if not api_key:
        return {
            "success": True,
            "image_bytes": generate_mock_image_bytes(),
            "error": None
        }
        
    if provider == "gemini":
        try:
            # Incorporate reference image context if present
            full_prompt = prompt
            if input_reference_image:
                full_prompt = f"{prompt}. Reference image style/layout context: {input_reference_image}"
                
            url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "instances": [{"prompt": full_prompt}],
                "parameters": {
                    "sampleCount": 1
                }
            }
            
            timeout = int(os.getenv("AI_GENERATION_TIMEOUT_SECONDS", "30"))
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "image_bytes": None,
                    "error": f"API Error (HTTP {response.status_code}): {response.text}"
                }
                
            res_data = response.json()
            images = res_data.get("generatedImages", [])
            if not images:
                return {
                    "success": False,
                    "image_bytes": None,
                    "error": "API returned empty response or no generated images."
                }
                
            b64_data = images[0].get("image", {}).get("imageBytes")
            if not b64_data:
                return {
                    "success": False,
                    "image_bytes": None,
                    "error": "No image data found in prediction response."
                }
                
            image_bytes = base64.b64decode(b64_data)
            return {
                "success": True,
                "image_bytes": image_bytes,
                "error": None
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "image_bytes": None,
                "error": "Provider API call timed out."
            }
        except Exception as e:
            return {
                "success": False,
                "image_bytes": None,
                "error": f"Unexpected provider error: {str(e)}"
            }
    else:
        return {
            "success": False,
            "image_bytes": None,
            "error": f"Unsupported AI provider: {provider}"
        }
