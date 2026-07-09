import datetime
from bson import ObjectId
from app.db import db
from app.config import Config
import google.generativeai as genai

class AIService:
    @staticmethod
    def compile_prompt(template, attributes):
        # Resolve placeholders in template, e.g. "A {font} neon sign in {color}"
        prompt = template
        for key, val in attributes.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(val))
        return prompt

    @classmethod
    def generate_preview(cls, user_id_str, category_id_str, selected_attributes):
        category = db.categories.find_one({"_id": ObjectId(category_id_str)})
        if not category:
            return None, "Category not found"
            
        template = category.get("ai_prompt_template", "Custom {text}")
        prompt = cls.compile_prompt(template, selected_attributes)
        
        # Build SVG mockup representation based on attributes
        text = selected_attributes.get("text", selected_attributes.get("name", "GALXY"))
        font = selected_attributes.get("font", "cursive")
        color = selected_attributes.get("color", "#FF2E8A")
        
        # Map color names to hex codes if name is supplied
        color_map = {
            "pink": "#FF2E8A",
            "magenta": "#FF2E8A",
            "blue": "#18E7FF",
            "electric_blue": "#18E7FF",
            "violet": "#9B5CFF",
            "yellow": "#FFD84D",
            "signal_yellow": "#FFD84D"
        }
        hex_color = color_map.get(str(color).lower(), str(color))
        if not hex_color.startswith("#"):
            hex_color = "#FF2E8A" # fallback
            
        # Map fonts
        font_family = "sans-serif"
        if font == "cursive":
            font_family = "'Brush Script MT', cursive, sans-serif"
        elif font == "bold":
            font_family = "'Arial Black', Impact, sans-serif"
        elif font == "modern":
            font_family = "'Space Grotesk', 'Inter', sans-serif"
            
        # Generate inline SVG preview image
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="blur1" />
      <feGaussianBlur stdDeviation="20" result="blur2" />
      <feMerge>
        <feMergeNode in="blur2" />
        <feMergeNode in="blur1" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <radialGradient id="bg-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{hex_color}" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#0B0B0F" stop-opacity="0"/>
    </radialGradient>
  </defs>
  
  <!-- Background -->
  <rect width="100%" height="100%" fill="#0B0B0F"/>
  <rect width="100%" height="100%" fill="url(#bg-glow)"/>
  
  <!-- Outer Glow Frame -->
  <rect x="50" y="50" width="700" height="400" rx="15" fill="none" stroke="{hex_color}" stroke-opacity="0.2" stroke-width="2" />
  <rect x="50" y="50" width="700" height="400" rx="15" fill="none" stroke="{hex_color}" stroke-width="4" filter="url(#glow)" opacity="0.6" />
  
  <!-- Custom Neon Text -->
  <text x="50%" y="260" font-family="{font_family}" font-size="72" font-weight="bold" fill="#F4F4F7" text-anchor="middle" filter="url(#glow)" stroke="{hex_color}" stroke-width="2" style="letter-spacing: 2px;">
    {text}
  </text>
  
  <!-- Accent Sign details -->
  <text x="50%" y="420" font-family="'Inter', sans-serif" font-size="14" fill="#8A8A97" text-anchor="middle" letter-spacing="4">
    GALXY CRAFT STUDIO PREVIEW
  </text>
</svg>"""

        # Convert to Data URI so we don't have network overhead in dev, 
        # or upload to Cloudinary if keys are present
        import base64
        svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        image_url = f"data:image/svg+xml;base64,{svg_base64}"
        
        # Check if Cloudinary is configured
        if Config.CLOUDINARY_CLOUD_NAME and Config.CLOUDINARY_API_KEY:
            try:
                import cloudinary
                import cloudinary.uploader
                cloudinary.config(
                    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
                    api_key=Config.CLOUDINARY_API_KEY,
                    api_secret=Config.CLOUDINARY_API_SECRET
                )
                
                # Upload the SVG Data URI directly to Cloudinary
                upload_res = cloudinary.uploader.upload(
                    image_url,
                    folder="galxy_ai_previews",
                    resource_type="image"
                )
                image_url = upload_res.get("secure_url")
            except Exception as e:
                print(f"Cloudinary upload failed: {str(e)}")
                
        # Call Gemini to log generated description if API key is present
        gemini_response_text = ""
        if Config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                sys_prompt = f"Write a one-sentence artistic lighting description for the custom craft product requested by this prompt: '{prompt}'."
                response = model.generate_content(sys_prompt)
                gemini_response_text = response.text.strip()
            except Exception as e:
                gemini_response_text = f"Failed to call Gemini API: {str(e)}"
                
        generation_doc = {
            "user_id": ObjectId(user_id_str) if user_id_str else None,
            "category_id": ObjectId(category_id_str),
            "prompt_used": prompt,
            "input_params": selected_attributes,
            "output_image_url": image_url,
            "gemini_description": gemini_response_text,
            "provider": "gemini",
            "status": "success",
            "created_at": datetime.datetime.utcnow()
        }
        
        res = db.ai_generations.insert_one(generation_doc)
        generation_doc["_id"] = str(res.inserted_id)
        if generation_doc["user_id"]:
            generation_doc["user_id"] = str(generation_doc["user_id"])
        generation_doc["category_id"] = str(generation_doc["category_id"])
        
        return generation_doc, None
