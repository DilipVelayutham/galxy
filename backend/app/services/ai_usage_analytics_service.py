from datetime import datetime
from bson import ObjectId

from app.db import db as real_db
import sys

db = real_db
if 'app' in sys.modules:
    app_mod = sys.modules['app']
    if hasattr(app_mod, 'db') and ('mock' in str(type(getattr(app_mod, 'db'))).lower()):
        db = getattr(app_mod, 'db')

class AIUsageAnalyticsService:
    @staticmethod
    def get_ai_usage_stats(category_id=None, date_from=None, date_to=None):
        """
        Retrieves AI Usage Analytics summary using MongoDB's aggregation pipelines:
        - total_generations, successful, failed (counts grouped by status)
        - cache_hit_rate (ratio of served_from_cache: true vs total, if present)
        - avg_generation_time_ms
        - generations_by_category (grouped by category_id, joined to categories collection)
        """
        if db is None:
            raise RuntimeError("Database connection module is not initialized by the Team Lead.")

        # 1. Build Match Stage for Filters
        match_filter = {}
        
        # Apply category filter if provided
        if category_id:
            try:
                # Check if it's a valid ObjectId, otherwise treat it as a string
                if ObjectId.is_valid(category_id):
                    match_filter['category_id'] = ObjectId(category_id)
                else:
                    match_filter['category_id'] = category_id
            except Exception:
                match_filter['category_id'] = category_id

        # Apply date filters (assuming field is 'created_at' or 'timestamp')
        date_filter = {}
        if date_from:
            try:
                # Support standard ISO-8601 strings
                date_filter['$gte'] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            except ValueError:
                pass
        if date_to:
            try:
                date_filter['$lte'] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            except ValueError:
                pass
                
        if date_filter:
            # We query the primary date field (assumed to be 'created_at' or 'timestamp')
            match_filter['created_at'] = date_filter

        # 2. Pipeline for Overview Statistics (total, successful, failed, avg time, cache hits)
        stats_pipeline = []
        if match_filter:
            stats_pipeline.append({'$match': match_filter})
            
        stats_pipeline.append({
            '$group': {
                '_id': None,
                'total_generations': {'$sum': 1},
                'successful': {
                    '$sum': {
                        '$cond': [{'$eq': ['$status', 'success']}, 1, 0]
                    }
                },
                'failed': {
                    '$sum': {
                        '$cond': [{'$eq': ['$status', 'failed']}, 1, 0]
                    }
                },
                # We sum cache hits to compute cache_hit_rate.
                'cache_hits': {
                    '$sum': {
                        '$cond': [{'$eq': ['$served_from_cache', True]}, 1, 0]
                    }
                },
                # We average generation time in milliseconds.
                'avg_generation_time_ms': {'$avg': '$generation_time_ms'}
            }
        })
        
        stats_result = list(db.ai_generations.aggregate(stats_pipeline))
        
        if stats_result:
            summary = stats_result[0]
            total = summary.get('total_generations', 0)
            successful = summary.get('successful', 0)
            failed = summary.get('failed', 0)
            avg_time = summary.get('avg_generation_time_ms', 0) or 0.0
            
            # Check if 'served_from_cache' actually exists in the collection to avoid fabrication.
            # If the collection is empty or the field is missing, cache_hit_rate will not be returned.
            sample_doc = db.ai_generations.find_one(match_filter) if db.ai_generations.count_documents(match_filter) > 0 else None
            has_served_from_cache = sample_doc is not None and 'served_from_cache' in sample_doc
            
            cache_hit_rate = None
            if has_served_from_cache and total > 0:
                cache_hit_rate = summary.get('cache_hits', 0) / total
        else:
            total = 0
            successful = 0
            failed = 0
            avg_time = 0.0
            cache_hit_rate = None
            
        # 3. Pipeline for Generations by Category (joining with the categories collection)
        category_pipeline = []
        if match_filter:
            category_pipeline.append({'$match': match_filter})
            
        category_pipeline.extend([
            {
                # Group by category_id to count generations
                '$group': {
                    '_id': '$category_id',
                    'count': {'$sum': 1}
                }
            },
            {
                # Join with categories collection
                '$lookup': {
                    'from': 'categories',
                    'localField': '_id',
                    'foreignField': '_id',
                    'as': 'category_info'
                }
            },
            {
                # Unwind category_info to make it a flat object
                '$unwind': {
                    'path': '$category_info',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                # Project fields into the requested format
                '$project': {
                    '_id': 0,
                    'category_id': {'$toString': '$_id'},
                    'category_name': {'$ifNull': ['$category_info.name', 'Unknown']},
                    'count': 1
                }
            }
        ])
        
        generations_by_category = list(db.ai_generations.aggregate(category_pipeline))
        
        response_data = {
            'total_generations': total,
            'successful': successful,
            'failed': failed,
            'avg_generation_time_ms': round(avg_time, 2),
            'generations_by_category': generations_by_category
        }
        
        # Include cache_hit_rate only if the served_from_cache field is verified to exist.
        if cache_hit_rate is not None:
            response_data['cache_hit_rate'] = round(cache_hit_rate, 4)
            
        return response_data
