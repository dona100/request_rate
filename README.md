# Django Request Rate Limiting Middleware

## Overview
This project implements a custom Django middleware to enforce request rate limiting based on IP addresses. It is designed to block IPs exceeding 100 requests in a rolling 5-minute window, ensuring efficient request handling even under high traffic.

---

## Features
- Tracks requests per IP using Django's caching framework (e.g., Redis or Memcached).
- Enforces a rolling window rate limit of 100 requests per 5 minutes.
- Returns HTTP 429 (Too Many Requests) status code for blocked IPs.
- Adds headers to responses indicating the remaining allowed requests and rate limit reset time.

---

## Implementation Details

### How Rolling Window Rate Limiting Works
1. **IP Address Tracking**:
   - Each incoming request is associated with the client's IP address.
2. **Caching**:
   - Requests are tracked using Django's caching framework.
   - The IP address serves as a unique cache key.
3. **Rate Limiting Logic**:
   - On each request:
     - If the cache key exists, the request count is incremented.
     - If the count exceeds 100 within 5 minutes, the request is blocked.
     - If the key doesn’t exist, a new entry is created with a count of 1 and a timestamp.
4. **Response Enhancements**:
   - Headers are added to indicate:
     - Remaining requests (`Remaining-Requests`).
     - Time until the limit resets (`RateLimit-Reset`).

### Testing Locally
1. **Setup**:
   - Ensure the middleware is added to the `MIDDLEWARE` list in `settings.py`.
   - Configure your cache backend .
2. **Send Requests**:
   - Use tools like Postman or `curl` to send requests to any endpoint.
   - Example using `curl`:
     ```bash
     curl -X GET http://127.0.0.1:8000/test/
     ```
3. **Observe Behavior**:
   - Within the limit (1–100 requests), the response will be `200 OK`.
   - After exceeding the limit, the response will be `429 Too Many Requests`.

---

## Example Input/Output

### Input
Simulate 101 requests:
```bash
for i in {1..101}; do curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/test/; done
