# API Rate Limiting Guide
**NexaCloud Support | Article ID: API-002 | Last Updated: 2025-06-01**

---

## Overview

Rate limiting protects the NexaCloud API from abuse and ensures fair usage across all customers. This guide explains rate limit values, how to check your current usage, and how to implement proper retry logic.

---

## 1. Rate Limit Tiers

### Plan-Based Limits

| Plan | Requests/Minute | Requests/Hour | Requests/Day | Burst (concurrent) |
|---|---|---|---|---|
| Starter | 100 | 2,000 | 10,000 | 10 |
| Professional | 1,000 | 20,000 | 500,000 | 50 |
| Business | 5,000 | 100,000 | 5,000,000 | 200 |
| Enterprise | Custom | Custom | Custom | Custom |

### Endpoint-Specific Limits
Some endpoints have additional rate limits:

| Endpoint | Limit |
|---|---|
| `POST /v1/auth/token` | 10 requests/minute per IP |
| `POST /v1/reports/generate` | 20 requests/minute per org |
| `POST /v1/exports/*` | 5 requests/minute per org |
| `GET /v1/audit-logs` | 60 requests/minute per org |
| `POST /v1/webhooks/*/events/*/retry` | 30 requests/minute per webhook |

---

## 2. Rate Limit Headers

Every API response includes rate limit information in the headers:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1717296000
X-RateLimit-Reset-After: 34
Retry-After: 34
```

| Header | Description |
|---|---|
| `X-RateLimit-Limit` | Maximum requests allowed in the current window |
| `X-RateLimit-Remaining` | Requests remaining in the current window |
| `X-RateLimit-Reset` | Unix timestamp when the limit resets |
| `X-RateLimit-Reset-After` | Seconds until the limit resets |
| `Retry-After` | Seconds to wait before retrying (only on 429 responses) |

---

## 3. Rate Limit Error Response

When you exceed the rate limit, you receive:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 34
X-RateLimit-Reset-After: 34
```

```json
{
  "error": {
    "code": "RATE_001",
    "message": "Rate limit exceeded. Too many requests in a short period.",
    "details": "Limit: 1000 requests/minute. 34 seconds until reset.",
    "request_id": "req_9f3a2b1c4d5e",
    "retry_after": 34
  }
}
```

---

## 4. Best Practices

### 1. Implement Exponential Backoff with Jitter

```python
import time
import random
import requests

def api_request_with_backoff(url: str, headers: dict, max_retries: int = 5):
    """Make an API request with exponential backoff on rate limit errors."""
    
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 429:
            # Use Retry-After header if available
            retry_after = int(response.headers.get('Retry-After', 2 ** attempt))
            
            # Add random jitter to prevent thundering herd
            jitter = random.uniform(0, 0.5 * retry_after)
            wait_time = retry_after + jitter
            
            print(f"Rate limited. Waiting {wait_time:.1f} seconds (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
        
        else:
            # Non-rate-limit error — don't retry
            response.raise_for_status()
    
    raise Exception(f"Max retries ({max_retries}) exceeded")
```

### 2. Monitor Your Usage Proactively

```python
def check_rate_limit_status(response):
    """Extract and log rate limit status from response headers."""
    remaining = int(response.headers.get('X-RateLimit-Remaining', -1))
    limit = int(response.headers.get('X-RateLimit-Limit', -1))
    reset_after = int(response.headers.get('X-RateLimit-Reset-After', 0))
    
    if remaining >= 0 and limit > 0:
        usage_percent = ((limit - remaining) / limit) * 100
        
        if usage_percent > 80:
            print(f"⚠️  Rate limit at {usage_percent:.0f}%. "
                  f"{remaining} requests remaining. Resets in {reset_after}s")
        
    return remaining, reset_after
```

### 3. Use Pagination Instead of Parallel Requests

```python
def paginate_all_results(endpoint: str, headers: dict):
    """Fetch all pages sequentially to respect rate limits."""
    results = []
    page = 1
    
    while True:
        response = requests.get(
            f"{endpoint}?page={page}&per_page=100",
            headers=headers
        )
        data = response.json()
        results.extend(data['data'])
        
        # Check if there are more pages
        pagination = data.get('pagination', {})
        if page >= pagination.get('total_pages', 1):
            break
        
        page += 1
        
        # Brief pause between pages to be a good API citizen
        time.sleep(0.1)
    
    return results
```

### 4. Cache Frequently Requested Data

- Cache responses for data that changes infrequently (e.g., org settings, user list)
- Respect `Cache-Control` and `ETag` headers in responses
- Use conditional requests with `If-None-Match` to avoid unnecessary data transfer

---

## 5. Checking Current Usage

### Via API
```http
GET /v1/usage/rate-limits
Authorization: Bearer YOUR_API_KEY
```

```json
{
  "plan": "Professional",
  "current_period": {
    "requests_made": 12847,
    "requests_limit": 500000,
    "reset_at": "2025-07-01T00:00:00Z"
  },
  "per_minute": {
    "requests_made": 87,
    "requests_limit": 1000,
    "reset_at": "2025-06-15T10:31:00Z"
  }
}
```

### Via Dashboard
1. Go to **Settings → API Keys**
2. Click on an API key
3. View the usage graph showing requests over time
4. See current period totals and limits

---

## 6. Enterprise Rate Limits

Enterprise customers can request custom rate limits based on their usage patterns. Contact sales@nexacloud.io or your Customer Success Manager.

Custom configurations available:
- Higher per-minute and per-day limits
- Dedicated rate limit pools per API key
- Priority queue access during high traffic periods
- SLA-backed response time guarantees

---

## 7. Frequently Asked Questions

**Q: Do rate limits apply to webhooks?**
A: No — rate limits apply to API requests you make. Incoming webhooks delivered to your server are not rate-limited, but the webhook delivery system itself has retry limits (see Webhook Documentation INT-004).

**Q: Are rate limits per API key or per organization?**
A: Rate limits are per **organization**, shared across all API keys in that organization.

**Q: Does read vs write affect rate limits?**
A: Currently all requests count equally. GET and POST requests both consume from the same rate limit pool.

**Q: Can I get temporary rate limit increases?**
A: Yes, for planned high-volume events (e.g., data migrations). Contact support 48 hours in advance with your planned usage pattern.

---

*Related articles: API Reference Guide (API-001), Error Codes Reference (API-003), Webhook Documentation (INT-004)*
