from flask import Blueprint, request, jsonify
from app.services.ai_usage_analytics_service import AIUsageAnalyticsService
from app.services.product_analytics_service import ProductAnalyticsService
from app.services.dashboard_service import get_dashboard_stats_data
from app.utils.auth import require_admin
import math
from app import db
# Define the blueprint for dashboard routes. All 4 members of Module 12 
# will register their routes under this blueprint or file.
admin_dashboard_bp = Blueprint('admin_dashboard', __name__)

@admin_dashboard_bp.route('/api/admin/analytics/ai-usage', methods=['GET', 'OPTIONS'])
@require_admin
def get_ai_usage_analytics():
    """
    GET /api/admin/analytics/ai-usage
    Fetches AI usage stats including total count, successful, failed, cache hit rate,
    average response time, and generations grouped by category.
    
    Query Parameters:
        - category_id (str): optional filter
        - date_from (str): optional start timestamp filter (ISO 8601 format)
        - date_to (str): optional end timestamp filter (ISO 8601 format)
    """
    try:
        # 1. Parse parameters from request query string
        category_id = request.args.get('category_id')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # 2. Query stats using the service
        stats = AIUsageAnalyticsService.get_ai_usage_stats(
            category_id=category_id,
            date_from=date_from,
            date_to=date_to
        )
        
        # 3. Return standardized project API response contract
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve AI usage analytics data.',
            'errors': [str(e)]
        }), 500


@admin_dashboard_bp.route('/api/admin/analytics/products', methods=['GET'])
@require_admin
def get_product_analytics():
    """
    GET /api/admin/analytics/products
    Fetches paginated product analytics including views, wishlist additions,
    order counts, and conversion rates.
    
    Query Parameters:
        - category_id (str): optional filter
        - date_from (str): optional ISO 8601 date to filter orders
        - date_to (str): optional ISO 8601 date to filter orders
        - sort (str): optional sorting ("views" | "wishlist_adds" | "orders")
        - page (int): page number for pagination, default 1
        - limit (int): count per page, default 10
    """
    try:
        category_id = request.args.get('category_id')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        sort = request.args.get('sort')
        
        # Parse pagination with safety fallbacks
        try:
            page = max(1, int(request.args.get('page', 1)))
        except (ValueError, TypeError):
            page = 1
            
        try:
            limit = max(1, int(request.args.get('limit', 10)))
        except (ValueError, TypeError):
            limit = 10
            
        data_list, total_count = ProductAnalyticsService.get_product_analytics(
            category_id=category_id,
            date_from=date_from,
            date_to=date_to,
            sort=sort,
            page=page,
            limit=limit
        )
        
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        
        return jsonify({
            'success': True,
            'data': data_list,
            'page': page,
            'limit': limit,
            'total': total_count,
            'totalPages': total_pages
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve product analytics data.',
            'errors': [str(e)]
        }), 500


@admin_dashboard_bp.route('/api/admin/dashboard/stats', methods=['GET', 'OPTIONS'])
@require_admin
def get_dashboard_stats():
    """
    GET /api/admin/dashboard/stats
    Fetches overarching admin dashboard statistics.
    """
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        stats = get_dashboard_stats_data(db, date_from_str=date_from, date_to_str=date_to)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve dashboard stats data.',
            'errors': [str(e)]
        }), 500
