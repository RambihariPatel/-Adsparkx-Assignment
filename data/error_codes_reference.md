# Error Codes Reference Guide
**NexaCloud Support | Article ID: API-003 | Last Updated: 2025-06-01**

---

## Overview

This reference lists all error codes returned by the NexaCloud API, their meanings, and recommended remediation steps. Errors follow RFC 7807 (Problem Details for HTTP APIs).

---

## Error Response Format

All API errors return a consistent JSON structure:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded the API rate limit.",
    "details": "Limit: 1000 requests/minute. Retry after 47 seconds.",
    "request_id": "req_9f3a2b1c4d5e",
    "documentation_url": "https://docs.nexacloud.io/errors/RATE_LIMIT_EXCEEDED"
  }
}
```

---

## HTTP Status Codes

| Status | Meaning |
|---|---|
| 200 OK | Request succeeded |
| 201 Created | Resource created successfully |
| 204 No Content | Request succeeded, no body returned |
| 400 Bad Request | Invalid request parameters |
| 401 Unauthorized | Missing or invalid authentication |
| 403 Forbidden | Valid auth, insufficient permissions |
| 404 Not Found | Resource does not exist |
| 409 Conflict | Resource conflict (e.g., duplicate) |
| 422 Unprocessable Entity | Validation errors |
| 429 Too Many Requests | Rate limit exceeded |
| 500 Internal Server Error | NexaCloud server error |
| 502 Bad Gateway | Upstream service error |
| 503 Service Unavailable | Temporary downtime |

---

## Authentication Errors (AUTH_xxx)

| Code | HTTP | Message | Solution |
|---|---|---|---|
| `AUTH_001` | 401 | Missing API key | Add `Authorization: Bearer YOUR_KEY` header |
| `AUTH_002` | 401 | Invalid API key | Verify key is correct and not revoked |
| `AUTH_003` | 401 | Expired API key | Rotate API key in Settings → API Keys |
| `AUTH_004` | 403 | Insufficient scope | Create a new key with required scopes |
| `AUTH_005` | 401 | JWT token expired | Refresh the access token |
| `AUTH_006` | 403 | IP not whitelisted | Add your IP to API key allowlist |
| `AUTH_007` | 403 | Account suspended | Contact billing@nexacloud.io |
| `AUTH_008` | 401 | MFA required | Complete MFA to obtain valid session token |

---

## Validation Errors (VAL_xxx)

| Code | HTTP | Message | Solution |
|---|---|---|---|
| `VAL_001` | 400 | Missing required field | Include all required parameters |
| `VAL_002` | 422 | Invalid email format | Use valid email format |
| `VAL_003` | 422 | Invalid date format | Use ISO 8601 (YYYY-MM-DDTHH:MM:SSZ) |
| `VAL_004` | 422 | Value out of range | Check min/max values in documentation |
| `VAL_005` | 422 | Invalid enum value | Use one of the allowed values listed |
| `VAL_006` | 400 | Request body too large | Max body size is 10MB |
| `VAL_007` | 422 | Invalid JSON | Validate request body JSON syntax |

---

## Resource Errors (RES_xxx)

| Code | HTTP | Message | Solution |
|---|---|---|---|
| `RES_001` | 404 | Resource not found | Verify the resource ID is correct |
| `RES_002` | 409 | Resource already exists | Use PUT to update instead of POST |
| `RES_003` | 403 | Resource access denied | Check user/API key permissions |
| `RES_004` | 409 | Resource is locked | Wait or release the lock |
| `RES_005` | 404 | Organization not found | Verify org slug in request |
| `RES_006` | 400 | Resource dependency missing | Create required parent resource first |

---

## Rate Limiting Errors (RATE_xxx)

| Code | HTTP | Message | Solution |
|---|---|---|---|
| `RATE_001` | 429 | Rate limit exceeded | Wait for Retry-After header value |
| `RATE_002` | 429 | Burst limit exceeded | Reduce concurrent requests |
| `RATE_003` | 429 | Daily quota exceeded | Upgrade plan or wait for quota reset |
| `RATE_004` | 429 | Organization rate limit | Coordinate usage across team |

See the Rate Limiting Guide (API-002) for limit values and retry strategies.

---

## Webhook Errors (WHK_xxx)

| Code | HTTP | Message | Solution |
|---|---|---|---|
| `WHK_001` | 400 | Invalid webhook URL | Must be HTTPS with valid certificate |
| `WHK_002` | 400 | Endpoint returned non-200 | Your server must return HTTP 200 within 10s |
| `WHK_003` | 400 | Signature verification failed | Check HMAC-SHA256 implementation |
| `WHK_004` | 404 | Webhook not found | Verify webhook ID |
| `WHK_005` | 409 | Duplicate webhook URL | Each endpoint URL must be unique |

---

## Integration Errors (INT_xxx)

| Code | HTTP | Message | Solution |
|---|---|---|---|
| `INT_001` | 400 | Integration credentials invalid | Re-authorize or update credentials |
| `INT_002` | 400 | OAuth token revoked | Re-authenticate the integration |
| `INT_003` | 503 | External service unavailable | Retry later or check third-party status |
| `INT_004` | 400 | Unsupported integration type | Check supported integrations list |
| `INT_005` | 409 | Integration already connected | Disconnect existing integration first |

---

## Server Errors (SRV_xxx)

| Code | HTTP | Message | Solution |
|---|---|---|---|
| `SRV_001` | 500 | Internal server error | Retry with exponential backoff; report if persistent |
| `SRV_002` | 503 | Service temporarily unavailable | Check status.nexacloud.io |
| `SRV_003` | 502 | Upstream dependency failed | Retry later |
| `SRV_004` | 500 | Database connection error | Retry with exponential backoff |

For persistent 5xx errors, contact support with your `request_id` from the error response.

---

## Best Practices for Error Handling

```python
import requests
import time

def api_call_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 429:
            # Respect Retry-After header
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Retrying in {retry_after}s...")
            time.sleep(retry_after)
        
        elif response.status_code in [500, 502, 503]:
            # Exponential backoff for server errors
            wait_time = (2 ** attempt) * 1
            print(f"Server error. Retrying in {wait_time}s...")
            time.sleep(wait_time)
        
        else:
            # Client error — don't retry
            error = response.json().get('error', {})
            raise Exception(f"API Error {error.get('code')}: {error.get('message')}")
    
    raise Exception("Max retries exceeded")
```

---

*Related articles: API Reference Guide (API-001), Rate Limiting Guide (API-002), Webhook Documentation (INT-004)*
