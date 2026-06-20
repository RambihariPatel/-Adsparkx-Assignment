# Account Management Guide
**NexaCloud Support | Article ID: ACC-002 | Last Updated: 2025-06-01**

---

## Overview

This guide explains how to manage your NexaCloud organization account — including user management, roles and permissions, organization settings, and data management.

---

## 1. Organization Settings

### Updating Organization Details
1. Navigate to **Settings → Organization**
2. Update fields: Organization name, industry, size, website
3. Click **"Save Changes"**

### Timezone Configuration
- Go to **Settings → Organization → Timezone**
- Select your primary timezone
- This affects all reporting, scheduled jobs, and notification times

> **Note:** Individual users can override the organization timezone in their personal profile.

---

## 2. User Management

### Inviting Users
1. Go to **Settings → Users & Permissions**
2. Click **"Invite User"**
3. Enter the user's email address
4. Select their role (see Role Definitions below)
5. Optionally restrict to specific Projects or Workspaces
6. Click **"Send Invitation"**

Invitation emails expire after **7 days**. You can resend from the Users list.

### Removing Users
1. Go to **Settings → Users & Permissions**
2. Click on the user's name
3. Click **"Remove User"**
4. Confirm removal

> **Note:** Removing a user does not delete their created content. Resources are transferred to the Admin who performed the removal.

### Deactivating vs Removing
- **Deactivate:** User cannot log in, data retained, seat freed up, can be reactivated
- **Remove:** User permanently removed from organization, cannot be undone without re-inviting

---

## 3. Roles & Permissions

### Built-In Roles

| Role | Access Level |
|---|---|
| **Owner** | Full access including billing, deletion of org, role assignment |
| **Admin** | Full access except billing and org deletion |
| **Manager** | Full access to assigned projects; cannot manage org settings |
| **Member** | Read and write within assigned projects |
| **Viewer** | Read-only access to assigned projects |
| **Billing Admin** | Access to billing settings only |

### Owner Role Constraints
- Only one Owner per organization
- Owner cannot be removed without transferring ownership first
- To transfer ownership: Settings → Organization → Transfer Ownership

### Custom Roles (Business & Enterprise Only)
1. Go to **Settings → Roles**
2. Click **"Create Custom Role"**
3. Define permissions at the module level (Projects, Users, Billing, API, Integrations)
4. Assign custom roles to users as needed

---

## 4. Projects & Workspaces

### Creating a Project
1. Click **"+ New Project"** on the main dashboard
2. Enter project name and description
3. Select visibility: Private (team only) or Internal (all org members)
4. Assign a project owner
5. Click **"Create Project"**

### Archiving a Project
- Go to the project → **Settings → Archive**
- Archived projects are read-only but data is retained
- Unarchive anytime from **Settings → Projects → Archived**

---

## 5. API Keys & Credentials

### Creating an API Key
1. Go to **Settings → API Keys**
2. Click **"Create API Key"**
3. Name your key and set an expiration date (optional)
4. Select scopes (permissions) for the key
5. Copy the key immediately — it is only shown once

### API Key Best Practices
- Never commit API keys to source control
- Use separate keys for each application/environment
- Rotate keys every 90 days
- Set minimal required scopes
- Use expiration dates for temporary integrations

### Revoking an API Key
1. Go to **Settings → API Keys**
2. Click **"Revoke"** next to the key
3. Confirm — this is immediate and permanent

---

## 6. Audit Logs (Business & Enterprise)

### Accessing Audit Logs
- Go to **Settings → Security → Audit Logs**
- Filter by user, action type, date range, or resource

### Logged Events Include
- User login/logout events
- User invitation, removal, role changes
- Project creation, deletion, archival
- API key creation, revocation
- Settings changes
- Billing changes
- Data export events
- SSO configuration changes

### Exporting Audit Logs
- Click **"Export"** to download as CSV
- API access available for programmatic export: `GET /v1/audit-logs`

---

## 7. Data Retention & Deletion

### Data Retention Periods
| Data Type | Retention Period |
|---|---|
| Active account data | Until account deletion |
| Deleted user data | 30 days |
| Audit logs | 1 year (Business) / 3 years (Enterprise) |
| Cancelled account data | 60 days post-cancellation |
| Deleted projects | 30 days (recoverable) |

### Requesting Data Export
1. Go to **Settings → Data & Privacy → Export Data**
2. Select data types and date range
3. Click **"Request Export"**
4. You will receive a download link via email within 24 hours

### Account Deletion
> **Warning:** Account deletion is permanent and irreversible after the grace period.

1. Only the **Owner** can delete an organization account
2. Go to **Settings → Organization → Danger Zone → Delete Organization**
3. Type the organization name to confirm
4. A 30-day grace period begins — data can be recovered within this window
5. Contact support@nexacloud.io to cancel deletion during grace period

---

*Related articles: Password Reset Guide (ACC-001), Two-Factor Authentication (ACC-005), Data Security Policy (SEC-001)*
