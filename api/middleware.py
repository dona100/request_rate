import time
from django.http import JsonResponse
from django.core.cache import cache

class RateLimitMiddleware:
    RATE_LIMIT = 100  # Max requests
    TIME_WINDOW = 300  # 5 minutes in seconds
    


    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        

        current_time = time.time()
        request_history = cache.get(ip, [])

        # Filter timestamps within the rolling window
        request_history = [ts for ts in request_history if current_time - ts <= self.TIME_WINDOW]

        # Check the rate limit
        if len(request_history) >= self.RATE_LIMIT:
            retry_after = int(self.TIME_WINDOW - (current_time - request_history[0]))
            return JsonResponse(
                {"error": "Too Many Requests"},
                status=429,
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.RATE_LIMIT),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Add the current timestamp and update cache
        request_history.append(current_time)
        cache.set(ip, request_history, timeout=self.TIME_WINDOW)
        request.META['RATE_LIMIT_REMAINING'] = self.RATE_LIMIT - len(request_history)

        response = self.get_response(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(request.META['RATE_LIMIT_REMAINING'])
        return response

    def get_client_ip(self, request):
        """Get the client's IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
