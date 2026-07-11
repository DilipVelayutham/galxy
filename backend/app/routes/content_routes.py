from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.db import db
from app.middleware.auth import require_admin, require_auth
import datetime

content_bp = Blueprint("content", __name__)

@content_bp.route("/site-content/<section>", methods=["GET"])
def get_site_content(section):
    content_doc = db.site_content.find_one({"section": section})
    
    if not content_doc:
        # Return default stubs if section doesn't exist yet
        stubs = {
            "hero": {
                "title": "GALXY Studio",
                "tagline": "Custom Lighting & Craft Studio",
                "description": "Bespoke neon boards, lamps, and quilling art.",
                "cta_text": "Configure Now",
                "cta_link": "/categories"
            },
            "about": {
                "story": "Welcome to GALXY, where light meets craft.",
                "artist_profile": "Led by artist Asil, hand-producing neon and acrylic masterpieces."
            },
            "contact": {
                "phone": "+91 99999 99999",
                "email": "asil@galxy.in",
                "instagram": "@galxy.in",
                "whatsapp": "9999999999"
            },
            "footer": {
                "copyright": "© 2026 GALXY Studio. All rights reserved.",
                "links": [{"label": "About", "url": "/about"}, {"label": "Contact", "url": "/contact"}]
            }
        }
        
        default_content = stubs.get(section, {})
        # Insert stub for future use
        db.site_content.insert_one({
            "section": section,
            "content": default_content,
            "updated_at": datetime.datetime.utcnow()
        })
        return jsonify({
            "success": True,
            "data": default_content
        }), 200
        
    return jsonify({
        "success": True,
        "data": content_doc.get("content", {})
    }), 200

@content_bp.route("/admin/site-content/<section>", methods=["PUT"])
@require_admin
def update_site_content(section):
    data = request.get_json() or {}
    content = data.get("content")
    
    if content is None:
        return jsonify({"success": False, "message": "content body is required"}), 400
        
    db.site_content.update_one(
        {"section": section},
        {
            "$set": {
                "content": content,
                "updated_at": datetime.datetime.utcnow()
            }
        },
        upsert=True
    )
    
    return jsonify({"success": True, "message": f"Section {section} updated successfully"}), 200

@content_bp.route("/admin/media/upload", methods=["POST"])
@require_auth
def upload_media():
    file = request.files.get("file")
    if not file:
        return jsonify({"success": False, "message": "No file uploaded"}), 400
        
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Configure cloudinary
        from app.config import Config
        cloudinary.config(
            cloud_name=Config.CLOUDINARY_CLOUD_NAME,
            api_key=Config.CLOUDINARY_API_KEY,
            api_secret=Config.CLOUDINARY_API_SECRET
        )
        
        res = cloudinary.uploader.upload(file)
        return jsonify({
            "success": True,
            "url": res.get("secure_url")
        }), 200
    except Exception as e:
        # Fallback local image link for mock testing
        mock_url = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
        return jsonify({
            "success": True,
            "url": mock_url,
            "message": f"Mock upload active (Dev Mode): {str(e)}"
        }), 200
