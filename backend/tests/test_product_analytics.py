import unittest
from unittest.mock import MagicMock, patch
import sys
from datetime import datetime

# Setup app/db mocks before importing service to avoid connection errors in tests
try:
    import app
    if not hasattr(app, 'db') or app.db is None:
        app.db = MagicMock()
except ImportError:
    from types import ModuleType
    app_mock = ModuleType('app')
    app_mock.db = MagicMock()
    sys.modules['app'] = app_mock
    import app

from app.services.product_analytics_service import ProductAnalyticsService

class TestProductAnalyticsService(unittest.TestCase):
    def setUp(self):
        from app.db import db
        db.products = MagicMock()
        db.wishlists = MagicMock()
        db.orders = MagicMock()
        db.categories = MagicMock()
        self.db = db

    def test_get_product_analytics_empty_db(self):
        """
        Verify that the service returns empty lists and zero total counts if products do not exist.
        """
        self.db.products.count_documents.return_value = 0
        
        data_list, total = ProductAnalyticsService.get_product_analytics()
        
        self.assertEqual(data_list, [])
        self.assertEqual(total, 0)
        self.db.products.aggregate.assert_not_called()

    def test_get_product_analytics_aggregations(self):
        """
        Verify that the pipelines run successfully and mathematical derivations are correct.
        """
        self.db.products.count_documents.return_value = 2
        
        # Mock result of the aggregation
        mock_aggregation_result = [
            {
                'product_id': 'prod1',
                'title': 'Luxury Lamp',
                'category_name': 'Lighting',
                'views': 100,
                'wishlist_count': 15,
                'order_count': 5,
                'conversion_rate': 0.05
            },
            {
                'product_id': 'prod2',
                'title': 'Craft Kit',
                'category_name': 'Crafts',
                'views': 200,
                'wishlist_count': 30,
                'order_count': 4,
                'conversion_rate': 0.02
            }
        ]
        self.db.products.aggregate.return_value = mock_aggregation_result
        
        data_list, total = ProductAnalyticsService.get_product_analytics(
            category_id='cat1',
            date_from='2026-07-01T00:00:00Z',
            date_to='2026-07-31T23:59:59Z',
            sort='views',
            page=1,
            limit=2
        )
        
        self.assertEqual(total, 2)
        self.assertEqual(len(data_list), 2)
        self.assertEqual(data_list[0]['product_id'], 'prod1')
        self.assertEqual(data_list[0]['views'], 100)
        self.assertEqual(data_list[0]['conversion_rate'], 0.05)
        self.assertEqual(data_list[1]['title'], 'Craft Kit')

        # Check that aggregate was called with matching elements
        self.db.products.aggregate.assert_called_once()
        pipeline = self.db.products.aggregate.call_args[0][0]
        
        # Verify stages in pipeline
        stages = [list(stage.keys())[0] for stage in pipeline]
        self.assertIn('$match', stages)
        self.assertIn('$lookup', stages)
        self.assertIn('$addFields', stages)
        self.assertIn('$project', stages)
        self.assertIn('$sort', stages)
        self.assertIn('$skip', stages)
        self.assertIn('$limit', stages)

    def test_pipeline_construction_with_date_filters(self):
        """
        Verify that date filters compile correctly inside the order pipeline logic.
        """
        self.db.products.count_documents.return_value = 1
        self.db.products.aggregate.return_value = []
        
        ProductAnalyticsService.get_product_analytics(
            date_from='2026-07-01T00:00:00Z',
            date_to='2026-07-10T23:59:59Z'
        )
        
        pipeline = self.db.products.aggregate.call_args[0][0]
        
        # Look for the order lookup stage
        order_lookup = None
        for stage in pipeline:
            if '$lookup' in stage and stage['$lookup'].get('from') == 'orders':
                order_lookup = stage['$lookup']
                break
                
        self.assertIsNotNone(order_lookup)
        lookup_pipeline = order_lookup['pipeline']
        
        # Verify lookup pipeline has match conditions for date ranges
        date_match = lookup_pipeline[0]['$match']
        self.assertIn('$or', date_match)
        self.assertIn('created_at', date_match['$or'][0])
        
        dt_from_filter = date_match['$or'][0]['created_at']['$gte']
        dt_to_filter = date_match['$or'][0]['created_at']['$lte']
        self.assertEqual(dt_from_filter, datetime.fromisoformat('2026-07-01T00:00:00+00:00'))
        self.assertEqual(dt_to_filter, datetime.fromisoformat('2026-07-10T23:59:59+00:00'))

if __name__ == '__main__':
    unittest.main()
