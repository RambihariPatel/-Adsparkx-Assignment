# Service Level Agreement (SLA) & Uptime Policy
**NexaCloud Support | Article ID: OPS-001 | Last Updated: 2025-06-01**

---

## Overview

NexaCloud is committed to providing a reliable, high-performance platform. This document outlines our uptime commitments, incident response process, and compensation policy for service disruptions.

---

## 1. Uptime Commitments by Plan

| Plan | Monthly Uptime SLA | Credits Eligible |
|---|---|---|
| Starter | 99.5% | No |
| Professional | 99.9% | Yes |
| Business | 99.95% | Yes |
| Enterprise | 99.99% | Yes — custom |

### Uptime Calculation
- Uptime % = ((Total minutes in month – Downtime minutes) / Total minutes in month) × 100
- Scheduled maintenance windows are **excluded** from downtime calculations
- Partial degradation (e.g., one region affected) counts as 50% downtime for affected customers

---

## 2. Scheduled Maintenance

- Maintenance windows: **Sundays, 2:00 AM – 4:00 AM IST**
- Advance notice: Minimum **72 hours** via email and status page
- Emergency maintenance: Minimum **2 hours** advance notice when possible

To subscribe to maintenance notifications:
1. Visit [status.nexacloud.io](https://status.nexacloud.io)
2. Click **"Subscribe to Updates"**
3. Choose email, Slack, or SMS notifications

---

## 3. Incident Response Times

### Support Response SLA

| Priority | Description | Starter | Professional | Business | Enterprise |
|---|---|---|---|---|---|
| P1 – Critical | Complete outage | 8 hrs | 4 hrs | 1 hr | 15 min |
| P2 – High | Major feature down | 24 hrs | 8 hrs | 2 hrs | 1 hr |
| P3 – Medium | Minor issue | 72 hrs | 24 hrs | 8 hrs | 4 hrs |
| P4 – Low | General inquiry | 5 days | 72 hrs | 24 hrs | 8 hrs |

*Response time = time to first meaningful response from NexaCloud support, not resolution time.*

### Priority Classification
**P1 – Critical:** Platform completely inaccessible, data loss occurring, security breach
**P2 – High:** Core features non-functional (e.g., API down, dashboards not loading for all users)
**P3 – Medium:** Non-core feature impaired, performance degraded, workaround available
**P4 – Low:** Minor cosmetic issues, documentation requests, general how-to questions

---

## 4. Status Page & Incident Communication

### Real-Time Status
- Check [status.nexacloud.io](https://status.nexacloud.io) for live system status
- Status components monitored:
  - API (Rest & GraphQL)
  - Web Application
  - Authentication Services
  - Webhook Delivery
  - Background Jobs
  - Data Sync Services

### Incident Update Cadence
| Phase | Update Frequency |
|---|---|
| Incident identified | Within 15 minutes of detection |
| Active incident | Every 30 minutes |
| Monitoring phase | Every 2 hours |
| Resolved | Post-incident report within 48 hours |

---

## 5. Service Credits

### Eligibility
Credits are available for Professional, Business, and Enterprise plans when:
- Monthly uptime falls below the SLA threshold
- The incident was caused by NexaCloud infrastructure
- A credit request is submitted within **30 days** of the incident

### Credit Calculation

| Uptime Achieved | Credit (% of monthly fee) |
|---|---|
| 99.0% – 99.89% (Professional) | 10% |
| 98.0% – 98.99% (Professional) | 25% |
| Below 98.0% (Professional) | 50% |
| 99.5% – 99.94% (Business) | 10% |
| 99.0% – 99.49% (Business) | 25% |
| Below 99.0% (Business) | 50% |
| Enterprise | Custom per contract |

### Maximum Credit
Credits do not exceed 50% of the monthly subscription fee for the affected month.
Credits are applied to the next billing cycle and are not payable as cash.

### Exclusions
Credits are **not** provided for downtime caused by:
- Customer's own actions or configurations
- Third-party service failures
- Force majeure events
- Scheduled maintenance
- Beta or experimental features

---

## 6. How to Request a Service Credit

1. Email **billing@nexacloud.io** with subject: "SLA Credit Request – [Month Year]"
2. Include:
   - Account email and Organization ID
   - Date and time of the incident (with timezone)
   - Duration of impact
   - Link to the relevant status page incident
3. NexaCloud will review and respond within 5 business days
4. Approved credits appear on your next invoice

---

## 7. Business Impact Assessment

For Enterprise customers, NexaCloud provides a quarterly Business Impact Report covering:
- Actual uptime achieved vs SLA
- Incident frequency and duration trends
- MTTR (Mean Time to Recover) metrics
- Recommendations for architecture resilience

Contact your Customer Success Manager to schedule this review.

---

*Related articles: Subscription Plans (BIL-002), Troubleshooting Guide (TRB-001), Status Page FAQ (OPS-002)*
