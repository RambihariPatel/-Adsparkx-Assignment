# Troubleshooting Guide — Common Issues
**NexaCloud Support | Article ID: TRB-001 | Last Updated: 2025-06-01**

---

## Overview

This guide helps you diagnose and resolve the most common issues encountered in NexaCloud. For API-specific errors, see the Error Codes Reference (API-003). For login issues, see Password Reset Guide (ACC-001).

---

## 1. Login & Authentication Issues

### Problem: "Invalid credentials" on correct password
**Possible causes:**
- Caps Lock is on
- Browser autofill is inserting wrong credentials
- Account email has a typo

**Steps:**
1. Type the password manually (don't paste)
2. Toggle Caps Lock off
3. Clear browser autofill for this site
4. Try an incognito/private browser window
5. If still failing, use Forgot Password to reset

### Problem: Page stuck after login / redirect loop
**Steps:**
1. Clear browser cookies and cache (Ctrl+Shift+Delete)
2. Disable browser extensions (especially ad blockers)
3. Try a different browser (Chrome, Firefox, Edge)
4. Check [status.nexacloud.io](https://status.nexacloud.io) for active incidents

### Problem: SSO login fails with "User not found"
**Steps:**
1. Confirm your email in the identity provider matches NexaCloud
2. Ask your IT admin to verify the SSO configuration
3. Ensure your organization's SSO domain mapping is correct in NexaCloud

---

## 2. Dashboard & UI Issues

### Problem: Dashboard not loading / blank screen
**Steps:**
1. Hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
2. Clear cache and cookies
3. Disable browser extensions
4. Ensure JavaScript is enabled
5. Check if the issue is browser-specific
6. If issue persists across browsers, contact support with your browser console log (F12 → Console → copy errors)

### Problem: Data not updating / stale data
**Steps:**
1. Click the refresh icon on the affected widget
2. Log out and back in
3. Check if your role/permissions have changed (Settings → Users)
4. Verify the data source integration is connected (Settings → Integrations)

### Problem: Notifications not appearing
**Steps:**
1. Check notification preferences: Settings → Notifications
2. Verify browser notifications are allowed for app.nexacloud.io
3. Check if email notifications are going to spam
4. For in-app notifications: refresh the page

---

## 3. Integration Issues

### Problem: Integration showing "Disconnected" status
**Steps:**
1. Go to Settings → Integrations → [Integration Name]
2. Click "Reconnect"
3. Re-authorize the connection (you'll be redirected to the third-party login)
4. If reconnect fails, delete the integration and re-add it fresh
5. Ensure the third-party account has not revoked NexaCloud permissions

### Problem: Data sync not working
**Steps:**
1. Check last sync timestamp in Settings → Integrations
2. Click "Force Sync" to manually trigger
3. Verify the integration credentials haven't expired
4. Check if the third-party service has rate-limited NexaCloud (check their status page)
5. Contact support with your integration ID and the sync error code

### Problem: Webhook events not being received
**Steps:**
1. Verify webhook URL is correct and publicly accessible
2. Check that your server returns HTTP 200 within 10 seconds
3. Review webhook logs: Settings → Integrations → Webhooks → [webhook name] → Logs
4. Check if failed events are being retried (NexaCloud retries up to 5 times with exponential backoff)
5. See the Webhook Documentation (INT-004) for payload structure

---

## 4. Performance Issues

### Problem: Application is slow / high latency
**Steps:**
1. Check your internet connection speed
2. Check [status.nexacloud.io](https://status.nexacloud.io) for performance degradation notices
3. Try from a different network (mobile hotspot)
4. Clear browser cache
5. If you're using the API, check if you're hitting rate limits (see Rate Limiting Guide)
6. For enterprise: contact support to check region-specific performance

### Problem: Reports taking too long to generate
**Steps:**
1. Reduce the date range in your report filters
2. Apply more specific filters to limit data volume
3. Schedule the report to run off-peak hours (before 8 AM or after 8 PM in your timezone)
4. Upgrade to a plan with higher compute resources for large data sets

---

## 5. Data & Export Issues

### Problem: CSV export is empty or incomplete
**Steps:**
1. Verify filters are not too restrictive
2. Check your account's data retention period (Settings → Billing)
3. Try exporting a smaller date range
4. If exporting via API, verify pagination is handled correctly

### Problem: Data appears incorrect / mismatched
**Steps:**
1. Verify the timezone setting: Settings → Organization → Timezone
2. Check if data is being displayed in UTC vs local time
3. Verify your integration sync is up to date
4. Contact support with specific data discrepancies (include timestamps)

---

## 6. Account & Billing Issues

### Problem: Charged for more than expected
**Steps:**
1. Check your invoice breakdown: Settings → Billing → Invoice History
2. Review seat count and usage-based charges
3. Check for prorated charges from a recent plan upgrade
4. If you believe it's an error, contact billing@nexacloud.io with your invoice number

### Problem: Can't add team members
**Steps:**
1. Verify you have an Admin role (Settings → Your Profile → Role)
2. Check your plan's seat limit (Settings → Billing → Plan Details)
3. If at seat limit, upgrade your plan or remove inactive users
4. Ensure you're inviting using the correct email format

---

## 7. Collecting Diagnostic Information for Support

When contacting support, please provide:
- **Browser and version** (Help → About in your browser)
- **Operating system**
- **Console logs** (F12 → Console → right-click → Save as)
- **Network logs** (F12 → Network → right-click → Save HAR)
- **Screenshot or screen recording** of the issue
- **Steps to reproduce** the issue
- **Affected user accounts or resource IDs**
- **Approximate time the issue started**
- **Organization ID** (found in Settings → Organization)

*Related articles: Error Codes Reference (API-003), Password Reset Guide (ACC-001), Status Page (OPS-001)*
