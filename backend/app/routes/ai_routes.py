from flask import Blueprint, request, jsonify, g
from bson import ObjectId
from app.services.ai_service import AIService
from app.middleware.auth import require_auth, require_admin, decode_token
from app.db import db
import datetime

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/generate-preview", methods=["POST"])
def generate_preview():
    data = request.get_json() or {}
    category_id = data.get("category_id")
    selected_attributes = data.get("selected_attributes", {})
    
    if not category_id:
        return jsonify({"success": False, "message": "category_id is required"}), 400
        
    # Check optional auth header for guest vs customer logging
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        try:
            token = auth_header.split(" ")[1]
            decoded = decode_token(token)
            if "error" not in decoded:
                user_id = decoded.get("user_id")
        except Exception:
            pass
            
    res, error = AIService.generate_preview(user_id, category_id, selected_attributes)
    if error:
        return jsonify({"success": False, "message": error}), 400
        
    return jsonify({
        "success": True,
        "message": "Preview generated successfully",
        "data": res
    }), 200

@ai_bp.route("/generations/<user_id>", methods=["GET"])
@require_auth
def get_user_generations(user_id):
    # Security check: users can only fetch their own history unless they are admin
    if g.user["id"] != user_id and g.user["role"] != "super_admin":
        return jsonify({"success": False, "message": "Unauthorized access to history"}), 403
        
    generations = list(db.ai_generations.find({"user_id": ObjectId(user_id)}).sort("created_at", -1))
    for gen in generations:
        gen["_id"] = str(gen["_id"])
        gen["user_id"] = str(gen["user_id"])
        gen["category_id"] = str(gen["category_id"])
        
    return jsonify({
        "success": True,
        "data": generations
    }), 200

@ai_bp.route("/admin/generations", methods=["GET"])
@require_admin
def get_admin_generations():
    generations = list(db.ai_generations.find().sort("created_at", -1).limit(100))
    for gen in generations:
        gen["_id"] = str(gen["_id"])
        if gen.get("user_id"):
            gen["user_id"] = str(gen["user_id"])
        gen["category_id"] = str(gen["category_id"])
        
    return jsonify({
        "success": True,
        "data": generations
    }), 200

@ai_bp.route("/admin/categories/<id>/ai-prompt-template", methods=["PUT"])
@require_admin
def update_category_prompt_template(id):
    data = request.get_json() or {}
    template = data.get("ai_prompt_template")
    
    if not template:
        return jsonify({"success": False, "message": "ai_prompt_template is required"}), 400
        
    res = db.categories.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"ai_prompt_template": template, "updated_at": datetime.datetime.utcnow()}}
    )
    
    if res.matched_count == 0:
        return jsonify({"success": False, "message": "Category not found"}), 404
        
    return jsonify({"success": True, "message": "AI prompt template updated successfully"}), 200
