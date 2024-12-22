from django.test import TestCase, Client
from django.core.cache import cache

class RateLimitMiddlewareTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.ip = '192.168.1.1'
    
    def test_rate_limiting(self):
        # Send 100 requests
        for _ in range(100):
            response = self.client.get('/test/', HTTP_X_FORWARDED_FOR=self.ip)
            self.assertEqual(response.status_code, 200)
        
        # 101st request should be blocked
        response = self.client.get('/test/', HTTP_X_FORWARDED_FOR=self.ip)
        self.assertEqual(response.status_code, 429)
        self.assertIn("Retry-After", response.headers)
    
    def test_rate_limit_reset(self):
        # Send requests and wait for reset
        for _ in range(100):
            self.client.get('/test/', HTTP_X_FORWARDED_FOR=self.ip)
        cache.clear()
        response = self.client.get('/test/', HTTP_X_FORWARDED_FOR=self.ip)
        self.assertEqual(response.status_code, 200)
