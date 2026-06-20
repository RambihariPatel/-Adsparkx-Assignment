# Integrations Guide
**NexaCloud Support | Article ID: INT-001 | Last Updated: 2025-06-01**

---

## Overview

NexaCloud connects with 50+ third-party tools, databases, and APIs. This guide covers integration setup, common configurations, troubleshooting, and best practices.

---

## 1. Supported Integrations

### Data Sources
| Integration | Type | Plans |
|---|---|---|
| Google Analytics 4 | Analytics | All |
| PostgreSQL | Database | Professional+ |
| MySQL | Database | Professional+ |
| Microsoft SQL Server | Database | Business+ |
| MongoDB | NoSQL | Business+ |
| BigQuery | Data Warehouse | Professional+ |
| Snowflake | Data Warehouse | Business+ |
| Amazon S3 | Object Storage | Professional+ |
| Google Cloud Storage | Object Storage | Professional+ |

### CRM & Sales
| Integration | Plans |
|---|---|
| Salesforce | Business+ |
| HubSpot | Professional+ |
| Pipedrive | Professional+ |
| Zoho CRM | Starter+ |

### Communication & Collaboration
| Integration | Plans |
|---|---|
| Slack | All |
| Microsoft Teams | Professional+ |
| Google Workspace | All |
| Notion | Professional+ |

### Automation
| Integration | Plans |
|---|---|
| Zapier | All |
| Make (Integromat) | Professional+ |
| n8n | Business+ |
| REST API (Custom) | All |
| Webhooks | All |

---

## 2. Setting Up an Integration

### Step-by-Step
1. Go to **Settings → Integrations**
2. Browse or search for the integration
3. Click **"Connect"** or **"Install"**
4. For OAuth integrations: Sign in to the third-party service and grant NexaCloud permissions
5. For API Key integrations: Enter your API key from the third-party service
6. For database integrations: Enter connection details (host, port, database name, credentials)
7. Configure sync settings:
   - **Sync frequency:** Real-time, every 15 min, hourly, daily
   - **Data scope:** Which data sets to include
   - **Field mapping:** How source fields map to NexaCloud fields
8. Click **"Test Connection"** to verify
9. Click **"Save & Activate"**

---

## 3. Database Connections

### PostgreSQL / MySQL Connection Settings

| Field | Description |
|---|---|
| Host | Database server IP or hostname |
| Port | Default: 5432 (PG), 3306 (MySQL) |
| Database Name | Name of the specific database |
| Username | Database user (use a read-only user for safety) |
| Password | Database password |
| SSL Mode | Required for cloud databases (require/verify-full) |

### Whitelisting NexaCloud IP Addresses
For databases behind a firewall, whitelist these NexaCloud static IPs:
- `34.100.215.12`
- `34.100.215.45`
- `34.100.215.89`
- `34.100.215.134`

> **Security Best Practice:** Create a dedicated read-only database user for NexaCloud with access only to the tables you need.

```sql
-- PostgreSQL: Create read-only user
CREATE USER nexacloud_reader WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE your_db TO nexacloud_reader;
GRANT USAGE ON SCHEMA public TO nexacloud_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO nexacloud_reader;
```

---

## 4. Slack Integration

### What Slack Integration Does
- Send dashboard alerts to Slack channels
- Receive workflow completion notifications
- Get daily/weekly report summaries
- Trigger NexaCloud actions from Slack commands (slash commands)

### Setting Up Slack
1. Go to **Settings → Integrations → Slack**
2. Click **"Add to Slack"**
3. Select your Slack workspace
4. Authorize NexaCloud
5. Choose a default notification channel
6. Click **"Save"**

### Configuring Alerts to Slack
1. Open any dashboard or report
2. Click the bell icon (Alerts)
3. Click **"Add Alert"**
4. Set conditions (e.g., metric drops below threshold)
5. Choose **Slack** as the notification channel
6. Select the target channel
7. Save the alert

---

## 5. REST API Integration

### Base URL
```
https://api.nexacloud.io/v1
```

### Authentication
All API requests require an API key in the header:
```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### Example: Fetch Projects
```http
GET /v1/projects
Authorization: Bearer YOUR_API_KEY
```

```json
{
  "data": [
    {
      "id": "proj_abc123",
      "name": "Marketing Analytics",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "total": 12,
    "page": 1,
    "per_page": 20
  }
}
```

### Supported API Operations
| Resource | Methods |
|---|---|
| Projects | GET, POST, PUT, DELETE |
| Dashboards | GET, POST, PUT, DELETE |
| Reports | GET, POST |
| Users | GET, POST, PUT, DELETE |
| Data Sources | GET, POST, PUT, DELETE |
| Webhooks | GET, POST, PUT, DELETE |
| Audit Logs | GET |

See the full API Reference Guide (API-001) for complete documentation.

---

## 6. Webhooks

### Setting Up Outgoing Webhooks
1. Go to **Settings → Integrations → Webhooks**
2. Click **"Add Webhook"**
3. Enter your endpoint URL (must be HTTPS)
4. Select events to subscribe to
5. Optionally add a secret for signature verification
6. Click **"Save"**

### Available Webhook Events
- `project.created` / `project.deleted`
- `report.generated` / `report.failed`
- `alert.triggered`
- `user.invited` / `user.removed`
- `integration.connected` / `integration.disconnected`
- `workflow.completed` / `workflow.failed`

### Webhook Security
NexaCloud signs all webhook payloads with HMAC-SHA256:
```python
import hmac, hashlib

def verify_signature(payload_body, secret, signature_header):
    expected = hmac.new(
        secret.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature_header)
```

See the Webhook Documentation (INT-004) for full details.

---

## 7. Common Integration Issues

### Integration shows "Error" status
1. Check if credentials have expired (re-authorize or update API key)
2. Verify the third-party service is operational
3. Check if permissions were revoked in the source system
4. Review integration logs: Settings → Integrations → [Name] → Logs

### Data not syncing
1. Click **"Force Sync"** to trigger a manual sync
2. Check sync frequency settings
3. Verify your plan supports the sync frequency you need
4. Review the data scope — filters may be excluding data

### Connection test fails
- Verify IP whitelist includes NexaCloud IPs (for database connections)
- Check SSL/TLS settings
- Confirm the credentials have the required permissions
- Test connectivity from outside NexaCloud if possible

---

*Related articles: API Reference Guide (API-001), Webhook Documentation (INT-004), Rate Limiting Guide (API-002)*
