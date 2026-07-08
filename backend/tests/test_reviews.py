# tests/test_reviews.py
import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
import mongomock

# Mock the database before importing blueprints or services
mock_db = mongomock.MongoClient().db
with patch('app.db.db', mock_db):
    from app.services.review_service import ReviewService
    from app.services.rating_rollup_service import RatingRollupService

class TestReviewsModule(unittest.TestCase):
    def setUp(self):
        # Clear collections
        mock_db.reviews.delete_many({})
        mock_db.products.delete_many({})
        mock_db.users.delete_many({})
        mock_db.orders.delete_many({})

    @patch('app.services.order_service.OrderService.has_delivered_order_for_product')
    def test_create_review_not_eligible(self, mock_eligibility):
        # 1. User has no delivered orders
        mock_eligibility.return_value = {"eligible": False}
        
        user_id = str(ObjectId())
        product_id = str(ObjectId())
        
        res, msg, code = ReviewService.create_review(user_id, product_id, 5, "Amazing neon!")
        
        self.assertIsNone(res)
        self.assertEqual(code, 403)
        self.assertIn("verified delivered purchase", msg)

    @patch('app.services.order_service.OrderService.has_delivered_order_for_product')
    def test_create_review_success_and_rollup(self, mock_eligibility):
        user_id = str(ObjectId())
        product_id = str(ObjectId())
        order_id = str(ObjectId())
        
        mock_eligibility.return_value = {
            "eligible": True,
            "order_id": order_id,
            "order_number": "GLX-1001"
        }
        
        # Mock product and user
        mock_db.users.insert_one({"_id": ObjectId(user_id), "name": "Rohan Sharma"})
        mock_db.products.insert_one({"_id": ObjectId(product_id), "title": "Custom Neon Board", "rating_avg": 0.0, "rating_count": 0})
        
        # 1. Create Review
        review, msg, code = ReviewService.create_review(user_id, product_id, 5, "Best lighting ever!", [])
        self.assertEqual(code, 201)
        self.assertIsNotNone(review)
        self.assertEqual(review["is_approved"], False)
        
        # Rollup average should still be 0 since review is not approved yet
        RatingRollupService.recalculate_product_rating(product_id)
        prod = mock_db.products.find_one({"_id": ObjectId(product_id)})
        self.assertEqual(prod["rating_avg"], 0.0)
        self.assertEqual(prod["rating_count"], 0)
        
        # 2. Approve Review
        approved, err = ReviewService.approve_review(review["_id"])
        self.assertIsNone(err)
        self.assertEqual(approved["is_approved"], True)
        
        # Rollup average should recalculate
        prod = mock_db.products.find_one({"_id": ObjectId(product_id)})
        self.assertEqual(prod["rating_avg"], 5.0)
        self.assertEqual(prod["rating_count"], 1)

    @patch('app.services.order_service.OrderService.has_delivered_order_for_product')
    def test_duplicate_review_prevention(self, mock_eligibility):
        user_id = str(ObjectId())
        product_id = str(ObjectId())
        order_id = str(ObjectId())
        
        mock_eligibility.return_value = {
            "eligible": True,
            "order_id": order_id,
            "order_number": "GLX-1001"
        }
        
        # Mock user
        mock_db.users.insert_one({"_id": ObjectId(user_id), "name": "Rohan"})
        
        # First submission
        res1, msg1, code1 = ReviewService.create_review(user_id, product_id, 4, "Cool sign")
        self.assertEqual(code1, 201)
        
        # Second submission (same user, product, order)
        res2, msg2, code2 = ReviewService.create_review(user_id, product_id, 5, "Super sign")
        self.assertIsNone(res2)
        self.assertEqual(code2, 409)
        self.assertIn("already reviewed", msg2)

if __name__ == '__main__':
    unittest.main()
