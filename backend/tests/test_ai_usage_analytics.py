import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the 'backend' directory to the path so tests can run from any working directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bson import ObjectId

import app
if not hasattr(app, 'db') or app.db is None:
    app.db = MagicMock()

# Now import the service we want to test
from app.services.ai_usage_analytics_service import AIUsageAnalyticsService

class TestAIUsageAnalyticsService(unittest.TestCase):
    def setUp(self):
        # Reset Mock databases and mock database tables before each test
        from app.db import db
        db.ai_generations = MagicMock()
        db.categories = MagicMock()
        self.db = db

    def test_get_ai_usage_stats_empty_db(self):
        """
        Verify that the service returns default/empty values if the database has no records.
        """
        self.db.ai_generations.aggregate.side_effect = [[], []]
        self.db.ai_generations.count_documents.return_value = 0
        
        result = AIUsageAnalyticsService.get_ai_usage_stats()
        
        self.assertEqual(result['total_generations'], 0)
        self.assertEqual(result['successful'], 0)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(result['avg_generation_time_ms'], 0.0)
        self.assertEqual(result['generations_by_category'], [])
        # cache_hit_rate should not be returned/fabricated if served_from_cache is absent
        self.assertNotIn('cache_hit_rate', result)

    def test_get_ai_usage_stats_with_data(self):
        """
        Verify that stats are summarized and cache_hit_rate is calculated if served_from_cache exists.
        """
        mock_overview = [{
            'total_generations': 50,
            'successful': 45,
            'failed': 5,
            'cache_hits': 10,
            'avg_generation_time_ms': 250.75
        }]
        mock_categories = [
            {'category_id': 'cat1', 'category_name': 'Code Generation', 'count': 30},
            {'category_id': 'cat2', 'category_name': 'Design Helpers', 'count': 20}
        ]
        
        # Setup mock db behaviors
        self.db.ai_generations.aggregate.side_effect = [mock_overview, mock_categories]
        self.db.ai_generations.count_documents.return_value = 1
        # Mock sample doc to contain served_from_cache field
        self.db.ai_generations.find_one.return_value = {'served_from_cache': True}
        
        result = AIUsageAnalyticsService.get_ai_usage_stats()
        
        self.assertEqual(result['total_generations'], 50)
        self.assertEqual(result['successful'], 45)
        self.assertEqual(result['failed'], 5)
        self.assertEqual(result['avg_generation_time_ms'], 250.75)
        self.assertEqual(result['cache_hit_rate'], 0.20) # 10 cache_hits / 50 total
        self.assertEqual(len(result['generations_by_category']), 2)
        self.assertEqual(result['generations_by_category'][0]['category_name'], 'Code Generation')

    def test_get_ai_usage_stats_without_cache_hits(self):
        """
        Verify that cache_hit_rate is omitted if served_from_cache is not present in data documents.
        """
        mock_overview = [{
            'total_generations': 10,
            'successful': 10,
            'failed': 0,
            'cache_hits': 0,
            'avg_generation_time_ms': 120.0
        }]
        
        self.db.ai_generations.aggregate.side_effect = [mock_overview, []]
        self.db.ai_generations.count_documents.return_value = 1
        # Mock find_one to NOT contain served_from_cache field
        self.db.ai_generations.find_one.return_value = {'status': 'success'} 
        
        result = AIUsageAnalyticsService.get_ai_usage_stats()
        
        self.assertNotIn('cache_hit_rate', result)

    @patch('app.services.ai_usage_analytics_service.db', None)
    def test_get_ai_usage_stats_database_not_initialized(self):
        """
        Verify that RuntimeError is raised if the database connection is None.
        """
        with self.assertRaises(RuntimeError):
            AIUsageAnalyticsService.get_ai_usage_stats()

    def test_get_ai_usage_stats_with_valid_filters(self):
        """
        Verify that category_id and date strings are parsed and matched correctly.
        """
        self.db.ai_generations.aggregate.side_effect = [[], []]
        self.db.ai_generations.count_documents.return_value = 0
        
        valid_cat_id = '64b1f4c5e3d7a82b98e12345'
        date_from = '2026-07-01T00:00:00Z'
        date_to = '2026-07-31T23:59:59Z'
        
        result = AIUsageAnalyticsService.get_ai_usage_stats(
            category_id=valid_cat_id,
            date_from=date_from,
            date_to=date_to
        )
        
        self.db.ai_generations.aggregate.assert_called()
        call_args = self.db.ai_generations.aggregate.call_args_list[0][0][0]
        match_stage = call_args[0]['$match']
        self.assertEqual(match_stage['category_id'], ObjectId(valid_cat_id))
        self.assertIn('created_at', match_stage)
        self.assertIn('$gte', match_stage['created_at'])
        self.assertIn('$lte', match_stage['created_at'])

    def test_get_ai_usage_stats_with_invalid_filters(self):
        """
        Verify that invalid category_id strings and malformed date strings are handled gracefully.
        """
        self.db.ai_generations.aggregate.side_effect = [[], []]
        self.db.ai_generations.count_documents.return_value = 0
        
        invalid_cat_id = 'invalid-id-string'
        invalid_date_from = 'not-a-date'
        invalid_date_to = 'not-a-date-either'
        
        result = AIUsageAnalyticsService.get_ai_usage_stats(
            category_id=invalid_cat_id,
            date_from=invalid_date_from,
            date_to=invalid_date_to
        )
        
        self.db.ai_generations.aggregate.assert_called()
        call_args = self.db.ai_generations.aggregate.call_args_list[0][0][0]
        match_stage = call_args[0]['$match']
        self.assertEqual(match_stage['category_id'], invalid_cat_id)
        self.assertNotIn('created_at', match_stage)

    @patch('bson.ObjectId.is_valid', side_effect=Exception("mocked exception"))
    def test_get_ai_usage_stats_filter_exception(self, mock_is_valid):
        """
        Verify that exceptions in ObjectId validation are handled gracefully.
        """
        self.db.ai_generations.aggregate.side_effect = [[], []]
        self.db.ai_generations.count_documents.return_value = 0
        
        result = AIUsageAnalyticsService.get_ai_usage_stats(category_id='some-id')
        self.db.ai_generations.aggregate.assert_called()
        call_args = self.db.ai_generations.aggregate.call_args_list[0][0][0]
        match_stage = call_args[0]['$match']
        self.assertEqual(match_stage['category_id'], 'some-id')

if __name__ == '__main__':
    unittest.main()
