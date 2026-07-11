from datetime import datetime
# pyrefly: ignore [missing-import]
from bson import ObjectId
import math

from app.db import db
class ProductAnalyticsService:
    @staticmethod
    def get_product_analytics(category_id=None, date_from=None, date_to=None, sort=None, page=1, limit=10):
        """
        Retrieves product analytics, combining product metadata with wishlist additions,
        orders (filtered by date range), and categories.

        Note: Verification of this pipeline is still pending against live data.

        Args:
            category_id (str, optional): ID of category to filter products.
            date_from (str, optional): ISO-8601 start date timestamp to filter orders.
            date_to (str, optional): ISO-8601 end date timestamp to filter orders.
            sort (str, optional): Field to sort by ("views", "wishlist_adds", "orders").
            page (int, optional): Page number for pagination. Defaults to 1.
            limit (int, optional): Number of items per page. Defaults to 10.

        Returns:
            tuple: (data_list, total_count)
        """
        # Use direct db import
            
        # 1. Build match filter for products
        match_filter = {}
        if category_id:
            try:
                if ObjectId.is_valid(category_id):
                    match_filter['category_id'] = ObjectId(category_id)
                else:
                    match_filter['category_id'] = category_id
            except Exception:
                match_filter['category_id'] = category_id

        # Get total count of matching products
        total_count = db.products.count_documents(match_filter)
        if total_count == 0:
            return [], 0
            
        # 2. Build Pipeline
        pipeline = []
        
        # Match stage for category_id filter
        if match_filter:
            pipeline.append({'$match': match_filter})
            
        # Wishlist Lookup: Match product _id (Object and String) against wishlists.product_ids
        wishlist_lookup = {
            '$lookup': {
                'from': 'wishlists',
                'let': {'prod_id_obj': '$_id', 'prod_id_str': {'$toString': '$_id'}},
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$or': [
                                    {'$in': ['$$prod_id_obj', {'$ifNull': ['$product_ids', []]}]},
                                    {'$in': ['$$prod_id_str', {'$ifNull': ['$product_ids', []]}]}
                                ]
                            }
                        }
                    }
                ],
                'as': 'wishlist_matches'
            }
        }
        pipeline.append(wishlist_lookup)
        
        # Calculate wishlist_count
        pipeline.append({
            '$addFields': {
                'wishlist_count': {'$size': '$wishlist_matches'}
            }
        })
        
        # Orders Lookup pipeline
        order_pipeline = []
        
        # Apply date filters inside order pipeline (uses indexing on date fields)
        date_filter = {}
        if date_from:
            try:
                # Standardize ISO-8601 strings
                parsed_from = date_from.replace('Z', '+00:00')
                if 'T' not in parsed_from:
                    parsed_from += 'T00:00:00+00:00'
                date_filter['$gte'] = datetime.fromisoformat(parsed_from)
            except ValueError:
                pass
        if date_to:
            try:
                parsed_to = date_to.replace('Z', '+00:00')
                if 'T' not in parsed_to:
                    parsed_to += 'T23:59:59+00:00'
                date_filter['$lte'] = datetime.fromisoformat(parsed_to)
            except ValueError:
                pass
                
        if date_filter:
            order_pipeline.append({
                '$match': {
                    '$or': [
                        {'created_at': date_filter},
                        {'timestamp': date_filter}
                    ]
                }
            })
            
        # Match product id inside orders
        order_pipeline.append({
            '$match': {
                '$expr': {
                    '$or': [
                        {'$in': ['$$prod_id_obj', {'$ifNull': ['$items.product_id', []]}]},
                        {'$in': ['$$prod_id_str', {'$ifNull': ['$items.product_id', []]}]}
                    ]
                }
            }
        })
        
        order_lookup = {
            '$lookup': {
                'from': 'orders',
                'let': {'prod_id_obj': '$_id', 'prod_id_str': {'$toString': '$_id'}},
                'pipeline': order_pipeline,
                'as': 'order_matches'
            }
        }
        pipeline.append(order_lookup)
        
        # Calculate order_count
        pipeline.append({
            '$addFields': {
                'order_count': {'$size': '$order_matches'}
            }
        })
        
        # Calculate conversion_rate (order_count / views)
        conversion_rate_calc = {
            '$addFields': {
                'conversion_rate': {
                    '$cond': [
                        {'$gt': [{'$ifNull': ['$views', 0]}, 0]},
                        {'$round': [{'$divide': ['$order_count', {'$ifNull': ['$views', 1]}]}, 4]},
                        0.0
                    ]
                }
            }
        }
        pipeline.append(conversion_rate_calc)
        
        # Categories Lookup
        category_lookup = {
            '$lookup': {
                'from': 'categories',
                'let': {'cat_id': '$category_id'},
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$or': [
                                    {'$eq': ['$_id', '$$cat_id']},
                                    {'$eq': [{'$toString': '$_id'}, '$$cat_id']}
                                ]
                            }
                        }
                    }
                ],
                'as': 'category_matches'
            }
        }
        pipeline.append(category_lookup)
        pipeline.append({
            '$unwind': {
                'path': '$category_matches',
                'preserveNullAndEmptyArrays': True
            }
        })
        
        # Projection Stage
        project_stage = {
            '$project': {
                '_id': 0,
                'product_id': {'$toString': '$_id'},
                'title': {'$ifNull': ['$title', 'Unknown Product']},
                'category_name': {'$ifNull': ['$category_matches.name', 'Unknown Category']},
                'views': {'$ifNull': ['$views', 0]},
                'wishlist_count': {'$ifNull': ['$wishlist_count', 0]},
                'order_count': {'$ifNull': ['$order_count', 0]},
                'conversion_rate': {'$ifNull': ['$conversion_rate', 0.0]}
            }
        }
        pipeline.append(project_stage)
        
        # Sorting Stage (Descending by default, stable sort with product_id)
        sort_mapping = {
            'views': 'views',
            'wishlist_adds': 'wishlist_count',
            'orders': 'order_count'
        }
        sort_field = sort_mapping.get(sort, 'views')
        pipeline.append({
            '$sort': {
                sort_field: -1,
                'product_id': 1
            }
        })
        
        # Pagination Skip & Limit
        skip_count = (page - 1) * limit
        pipeline.append({'$skip': skip_count})
        pipeline.append({'$limit': limit})
        
        # Execute aggregate query
        data_list = list(db.products.aggregate(pipeline))
        
        return data_list, total_count
