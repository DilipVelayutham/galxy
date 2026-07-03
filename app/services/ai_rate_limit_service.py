from datetime import datetime
from bson import ObjectId
from app.configs.ai_config import AIConfig

def check_rate_limit(user_id, session_id):
    try:
        from app.models.ai_generation import AIGeneration
        col = AIGeneration.get_collection()
        
        # 1. Authenticated User Rate Limiting (Daily Cap)
        if user_id:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            user_count = col.count_documents({
                "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
                "status": {"$in": ["success", "failed"]},
                "created_at": {"$gte": today_start}
            })
            
            if user_count >= AIConfig.AI_MAX_GENERATIONS_PER_USER_PER_DAY:
                return {
                    "allowed": False,
                    "limit_reached": True,
                    "limit_scope": "user"
                }
                
        # 2. Guest Session Rate Limiting (Total Free Generations)
        elif session_id:
            session_count = col.count_documents({
                "session_id": session_id,
                "status": {"$in": ["success", "failed"]}
            })
            
            if session_count >= AIConfig.AI_FREE_GENERATIONS_PER_SESSION:
                return {
                    "allowed": False,
                    "limit_reached": True,
                    "limit_scope": "session"
                }
                
    except Exception:
        # Fail open: Do not block users if Mongo query fails
        pass
        
    return {
        "allowed": True,
        "limit_reached": False,
        "limit_scope": None
    }
