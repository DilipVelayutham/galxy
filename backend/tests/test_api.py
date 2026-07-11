import os
import sys
import unittest
import json

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from app.db import db
from app.services.pricing_service import calculate_custom_price

class AntiGravityBackendTests(unittest.TestCase):
    def setUp(self):
        # Configure Flask app for testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Keep a copy of fallback DB if it exists, or prepare a clean test database state
        self.original_settings = db.get_admin_settings()

    def test_price_calculation_formula(self):
        # Test default configuration price calculation
        # Base: 99.0, Size: 100, Text: "GALXY" (5 * 2.0 = 10.0), Float: 5 (5 * 5.0 = 25.0), Glow: #00f3ff (0.0)
        # Expected: 99.0 + 0 + 0 + 10.0 + 25.0 = 134.0
        config = {
            "size": 100,
            "glow_color": "#00f3ff",
            "design_text": "GALXY",
            "float_intensity": 5
        }
        price = calculate_custom_price(config, self.original_settings)
        self.assertEqual(price, 134.0)

        # Test large size (+20% size scale)
        # Size: 120 (adds 20 * $1.0 = $20.0)
        # Expected: 134.0 + 20.0 = 154.0
        config_large = {
            "size": 120,
            "glow_color": "#00f3ff",
            "design_text": "GALXY",
            "float_intensity": 5
        }
        price_large = calculate_custom_price(config_large, self.original_settings)
        self.assertEqual(price_large, 154.0)

        # Test premium glow color (+15.0)
        # Glow: #ff0055 (adds 15.0)
        # Expected: 134.0 + 15.0 = 149.0
        config_glow = {
            "size": 100,
            "glow_color": "#ff0055",
            "design_text": "GALXY",
            "float_intensity": 5
        }
        price_glow = calculate_custom_price(config_glow, self.original_settings)
        self.assertEqual(price_glow, 149.0)

    def test_api_price_endpoint(self):
        payload = {
            "size": 100,
            "glow_color": "#00f3ff",
            "design_text": "HELLOWORLD",  # 10 chars = +$20.0
            "float_intensity": 2           # Level 2 = +$10.0
        }
        # Expected: 99.0 (base) + 20.0 (text) + 10.0 (float) = 129.0
        response = self.client.post('/api/price', 
                                    data=json.dumps(payload),
                                    content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['price'], 129.0)

    def test_api_config_crud_flow(self):
        # Create a new design configuration
        payload = {
            "preset": "orb",
            "preset_name": "Gravity Orb",
            "size": 110,
            "glow_color": "#ff9900",
            "design_text": "TEST",
            "float_intensity": 8,
            "rotation_angle": 45
        }
        
        # Save config
        response_save = self.client.post('/api/config', 
                                         data=json.dumps(payload),
                                         content_type='application/json')
        data_save = json.loads(response_save.data)
        
        self.assertEqual(response_save.status_code, 200)
        self.assertTrue(data_save['success'])
        saved_id = data_save['configuration']['id']
        self.assertIsNotNone(saved_id)

        # Get configs
        response_get = self.client.get('/api/config')
        data_get = json.loads(response_get.data)
        self.assertEqual(response_get.status_code, 200)
        self.assertTrue(data_get['success'])
        
        # Verify the saved design exists in configurations
        found = any(c['id'] == saved_id for c in data_get['configurations'])
        self.assertTrue(found)

        # Delete config
        response_del = self.client.delete(f'/api/config/{saved_id}')
        data_del = json.loads(response_del.data)
        self.assertEqual(response_del.status_code, 200)
        self.assertTrue(data_del['success'])

        # Verify it has been deleted
        response_get_after = self.client.get('/api/config')
        data_get_after = json.loads(response_get_after.data)
        found_after = any(c['id'] == saved_id for c in data_get_after['configurations'])
        self.assertFalse(found_after)

    def test_api_admin_settings_flow(self):
        new_settings = {
            "base_price": 120.0,
            "size_price_per_percent": 1.5,
            "text_price_per_char": 3.0,
            "float_price_per_level": 7.0,
            "color_prices": {
                "#00f3ff": 1.0,
                "#ff0055": 20.0,
                "#00ff66": 12.0,
                "#ff9900": 15.0,
                "#0066ff": 6.0
            }
        }
        
        # Update settings
        response_update = self.client.post('/api/admin/settings',
                                           data=json.dumps(new_settings),
                                           content_type='application/json')
        data_update = json.loads(response_update.data)
        self.assertEqual(response_update.status_code, 200)
        self.assertTrue(data_update['success'])
        self.assertEqual(data_update['settings']['base_price'], 120.0)

        # Re-fetch settings
        response_get = self.client.get('/api/admin/settings')
        data_get = json.loads(response_get.data)
        self.assertEqual(response_get.status_code, 200)
        self.assertEqual(data_get['settings']['base_price'], 120.0)
        self.assertEqual(data_get['settings']['color_prices']['#ff0055'], 20.0)

        # Reset back to original to avoid corrupting data
        db.update_admin_settings(self.original_settings)

if __name__ == '__main__':
    unittest.main()
