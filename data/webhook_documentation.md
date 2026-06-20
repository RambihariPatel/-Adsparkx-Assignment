# Webhook Documentation
**NexaCloud Support | Article ID: INT-004 | Last Updated: 2025-06-01**

---

## Overview

Webhooks allow NexaCloud to push real-time notifications to your server when events occur in your account. Instead of polling the API, your server receives instant HTTP POST requests with event data.

---

## 1. Setting Up Webhooks

### Via Dashboard
1. Go to **Settings → Integrations → Webhooks**
2. Click **"Add Webhook"**
3. Enter your **Endpoint URL** (must be HTTPS with valid SSL certificate)
4. Select the **events** you want to subscribe to
5. Optionally add a **secret** for signature verification (recommended)
6. Click **"Save"**

### Via API
```http
POST /v1/webhooks
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "url": "https://your-server.com/webhooks/nexacloud",
  "events": ["project.created", "report.generated", "alert.triggered"],
  "secret": "your_webhook_secret",
  "active": true,
  "description": "Production webhook"
}
```

**Response:**
```json
{
  "id": "wh_abc123xyz",
  "url": "https://your-server.com/webhooks/nexacloud",
  "events": ["project.created", "report.generated", "alert.triggered"],
  "active": true,
  "created_at": "2025-06-01T10:00:00Z"
}
```

---

## 2. Available Events

### Project Events
| Event | Triggered When |
|---|---|
| `project.created` | A new project is created |
| `project.updated` | Project settings are modified |
| `project.deleted` | A project is deleted |
| `project.archived` | A project is archived |

### Report Events
| Event | Triggered When |
|---|---|
| `report.generated` | A report completes successfully |
| `report.failed` | A report generation fails |
| `report.scheduled` | A scheduled report is set up |

### User Events
| Event | Triggered When |
|---|---|
| `user.invited` | A user invitation is sent |
| `user.joined` | A user accepts an invitation |
| `user.removed` | A user is removed from the org |
| `user.role_changed` | A user's role is updated |

### Integration Events
| Event | Triggered When |
|---|---|
| `integration.connected` | An integration is successfully connected |
| `integration.disconnected` | An integration is removed or loses auth |
| `integration.sync_completed` | A data sync finishes |
| `integration.sync_failed` | A data sync fails |

### Alert Events
| Event | Triggered When |
|---|---|
| `alert.triggered` | An alert condition is met |
| `alert.resolved` | An alert condition clears |

### Workflow Events
| Event | Triggered When |
|---|---|
| `workflow.started` | A workflow begins execution |
| `workflow.completed` | A workflow finishes successfully |
| `workflow.failed` | A workflow encounters an error |

---

## 3. Webhook Payload Structure

All webhook payloads follow this structure:

```json
{
  "id": "evt_9f3a2b1c4d5e6f7g",
  "event": "project.created",
  "created_at": "2025-06-01T10:30:00Z",
  "organization_id": "org_abc123",
  "data": {
    // Event-specific data
  }
}
```

### Example: `project.created` Payload
```json
{
  "id": "evt_9f3a2b1c4d5e6f7g",
  "event": "project.created",
  "created_at": "2025-06-01T10:30:00Z",
  "organization_id": "org_abc123",
  "data": {
    "project": {
      "id": "proj_xyz789",
      "name": "Q2 Marketing Analytics",
      "visibility": "private",
      "created_by": {
        "id": "usr_def456",
        "email": "john@company.com",
        "name": "John Smith"
      }
    }
  }
}
```

### Example: `alert.triggered` Payload
```json
{
  "id": "evt_alert789",
  "event": "alert.triggered",
  "created_at": "2025-06-01T14:22:00Z",
  "organization_id": "org_abc123",
  "data": {
    "alert": {
      "id": "alrt_123",
      "name": "Revenue Drop Alert",
      "condition": "revenue < 10000",
      "current_value": 8500,
      "threshold": 10000,
      "dashboard_id": "dash_456"
    }
  }
}
```

---

## 4. Webhook Security

### Signature Verification (Recommended)
NexaCloud signs every webhook payload using HMAC-SHA256 with your webhook secret. Always verify signatures to ensure payloads are genuinely from NexaCloud.

**Signature Header:** `X-NexaCloud-Signature: sha256=<signature>`

#### Python Verification
```python
import hmac
import hashlib

def verify_nexacloud_signature(payload_body: bytes, secret: str, signature_header: str) -> bool:
    """
    Verify that the webhook payload came from NexaCloud.
    
    Args:
        payload_body: Raw bytes of the request body
        secret: Your webhook secret
        signature_header: Value of X-NexaCloud-Signature header
    
    Returns:
        True if signature is valid, False otherwise
    """
    expected_signature = hmac.new(
        key=secret.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    expected = f"sha256={expected_signature}"
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected, signature_header)
```

#### Node.js Verification
```javascript
const crypto = require('crypto');

function verifyNexaCloudSignature(payloadBody, secret, signatureHeader) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payloadBody)
    .digest('hex');
  
  const expected = `sha256=${expectedSignature}`;
  
  return crypto.timingSafeEqual(
    Buffer.from(expected),
    Buffer.from(signatureHeader)
  );
}
```

---

## 5. Delivery & Retry Logic

### Delivery Behavior
- NexaCloud makes a **POST request** to your endpoint URL
- Your server must return **HTTP 200** within **10 seconds**
- Any other HTTP status code (4xx, 5xx) or timeout is treated as a failure

### Retry Schedule
Failed deliveries are retried automatically:

| Attempt | Delay After Previous |
|---|---|
| 1st retry | 5 minutes |
| 2nd retry | 30 minutes |
| 3rd retry | 2 hours |
| 4th retry | 8 hours |
| 5th retry | 24 hours |

After 5 failed retries, the event is marked as permanently failed and no further retries occur.

### Manual Retry
In the dashboard:
1. Go to **Settings → Integrations → Webhooks**
2. Select your webhook
3. Click **"Event Logs"**
4. Find the failed event and click **"Retry"**

Via API:
```http
POST /v1/webhooks/{webhook_id}/events/{event_id}/retry
Authorization: Bearer YOUR_API_KEY
```

---

## 6. Testing Webhooks

### Dashboard Test
1. Go to **Settings → Integrations → Webhooks**
2. Select your webhook
3. Click **"Send Test Event"**
4. Choose an event type
5. A test payload is sent immediately to your endpoint

### Local Testing with ngrok
For local development, use ngrok to expose your local server:
```bash
# Install ngrok and authenticate
ngrok http 3000

# Your webhook URL would be something like:
# https://abc123.ngrok.io/webhooks/nexacloud
```

---

## 7. Viewing Webhook Logs

1. Go to **Settings → Integrations → Webhooks**
2. Click on your webhook name
3. Click **"Event Logs"** tab

Logs show:
- Event ID and type
- Delivery timestamp
- HTTP status code returned
- Response body (truncated)
- Delivery duration
- Number of retries

Logs are retained for **30 days**.

---

*Related articles: Integrations Guide (INT-001), Rate Limiting Guide (API-002), Error Codes Reference (API-003)*
